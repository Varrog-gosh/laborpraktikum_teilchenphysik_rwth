#!/usr/bin/python
# -*- coding: utf-8 -*-

import ROOT
import numpy
from tools import *
from Styles import tdrStyle
from kalibration import *
tdrStyle()

def normedHist( name, color, func = 0):
	if func == 0:
		hist = tkaToHist( name, 2000, 16000 )
		hist.Rebin(50)
	else:
		# let's hope func is a TF1
		hist = tkaToTimeHist(name, func , -2, 8 )
	hist.Scale(1./hist.Integral())
	hist.GetYaxis().SetTitle("Normierte Eintr#ddot{a}ge")
	hist.SetLineColor( color )
	hist.SetMarkerStyle( 23 + color )
	hist.SetMarkerSize( 1.5 )
	hist.SetMarkerColor( color )
	return hist


func = kalibration()
alutime = normedHist( 'data/aluminium.TKA', 3, func )
polytime = normedHist( 'data/poly.TKA', 4, func )
cotime = normedHist( 'data/co60.TKA', 1, func )


alu = normedHist( 'data/aluminium.TKA', 2, 0 )
poly = normedHist( 'data/poly.TKA', 4, 0 )
co = normedHist( 'data/co60.TKA', 1, 0 )


#co2time = normedHist( 'data/co60_2.TKA', 12 , func )


def histToArray( histo ):
	'''
	converts a histogram to numpy.array
	'''
	from numpy import array
	nbins = histo.GetNbinsX()
	values = array( [0] * nbins, dtype = 'f' )
	for i in range( nbins ):
		values[i] = histo.GetBinContent(i + 1)
	return values


def calculateDeconvolution( signal, background , signalname, backgroundname ):
	'''
	using roots deconvolution class
	signal: histogram containing measured signal data
	background: usually cobalt histogramm
	*names: names in legend for distributions

	returns: void
	'''
	from ROOT import TH1D,TSpectrum, TF1,TCanvas,TLegend
	for hist in [signal, background]:
		# this is cheating
		hist.GetXaxis().Set( hist.GetXaxis().GetNbins(), -2,8)
		#hist.Scale(1./hist.Integral())
		hist.SetXTitle('t [ns]')
		hist.Rebin(2)
		hist.GetXaxis().SetRangeUser( -20,20)

	can = TCanvas( randomName(), 'Deconvolution', 1400, 800 )
	can.cd()
	can.SetBatch()
	can.SetLogy()

	source = histToArray( signal )
	response = histToArray( background )
	s = TSpectrum();
	# parameters for deconvolution:
	# iterations = 1: more iterations -> stange peaks and more noice
	# repetitions =  1: same as above
	# boosting factor = 1: not needed
	s.Deconvolution(source, response, len( source ), 1, 1, 0 )

	signal.SetMinimum(1e-6)
	signal.Draw("P")
	background.Draw("sameP")

	d = signal.Clone()
	d.SetLineColor(2)

	for i in range( len(source) ):
		d.SetBinContent(i + 1,source[i])
	d.Draw("same,hist")

	leg = TLegend(0.6, 0.7, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( signal, signalname, "lp")
	leg.AddEntry( background, backgroundname, "lp")
	leg.AddEntry( d, "Entfaltung des Spektrums", "l")
	leg.Draw()

	can.SaveAs("deconvolution.pdf")
	return d



def twoLinearFits( signal, saveAffix, ranges):
	'''
	fits two linear functions to the signal distribution
	signal: histogram containing data
	ranges: list of tuples. Each tuple contains minimum and maximum of fit

	returns: void, prints two pdfs
	'''
	from ROOT import TF1, TCanvas, TLegend, TPaveText, TLine

	# take logarithm of histogram
	from math import log
	for i in range( signal.GetXaxis().GetNbins() + 1 ):
		signal.SetBinError( i, signal.GetBinError(i) / signal.GetBinContent(i) )
		if signal.GetBinContent(i) > 0:
			signal.SetBinContent( i, log( signal.GetBinContent(i) ) )
		else:
			signal.SetBinContent( i, log( 1e-19) )

	for i, ran in enumerate( ranges ):
		can = TCanvas( 'linear', "dualliniar", 700, 1000 )
		can.SetBatch()
		can.Divide(1,2)
		can.cd(1)

		s = signal.Clone()
		s.GetYaxis().SetTitle('ln( Eintr#ddot{a}ge )')
		s.SetAxisRange( ran[0] - 0.5, ran[1] + 0.5 )
		fit = TF1('mypol1', 'pol1', ran[0], ran[1] )
		res = signal.Clone()
		s.Fit('mypol1','r')
		s.SetStats(0)
		s.Draw()

		# Draw box with infos
		func = s.GetFunction('mypol1')
		info = TPaveText(0.5,.7, .9,.9, 'ndc')
		info.SetFillColor(0)
		info.SetLineColor(0)
		info.SetShadowColor(0)
		info.AddText( '#chi^{{2}} / NDF = {} / {}'.format(int(func.GetChisquare()), func.GetNDF()) )
		from re import sub
		print ' & {} - {} & {} &\\\\'.format(ran[0], ran[1],printError(-1/func.GetParameter(1), func.GetParError(1)/(func.GetParameter(1))**2))
		info.AddText( '#tau_{'+str(i+1)+'} = ' + sub('±', "#pm", printError(-1/func.GetParameter(1), func.GetParError(1)/(func.GetParameter(1))**2, 'ns')))
		info.Draw()

		# Compute and draw residuals, not working now
		can.cd(2)
		res.SetAxisRange( ran[0], ran[1] )
		for j in range( res.GetXaxis().GetNbins() +1 ):
			res.SetBinContent( j, res.GetBinContent(j) - func.Eval( res.GetBinCenter(j) ) )
		res.SetYTitle('Residuen')
		res.Draw()
		line = TLine( ran[0], 0,  ran[1] ,0)
		line.Draw()

		can.SaveAs('linearFit{}{}.pdf'.format( saveAffix, i ) )
		can.Close()

def linear_and_centroid (signal,background,signalname):
	'''
	fit linear functions to the tail of signal distribution
	substract long lifetime component
	perform second linear fit and also try centroid shift method

	returns: void, prints two pdfs
	'''
	from ROOT import TF1, TCanvas, TLegend, TPaveText, TLine ,TPaveStats

	can = TCanvas( 'linear', "Tail Anpassung", 1300, 800 )
	can.SetBatch()
	

	s = signal.Clone()
	# take logarithm of histogram
	from math import log,exp
	for i in range( signal.GetXaxis().GetNbins() + 1 ):
		s.SetBinError( i, s.GetBinError(i) / s.GetBinContent(i))
		if s.GetBinContent(i) < 0.0:
			content = abs(s.GetBinContent(i+1) + s.GetBinContent(i-1))/2
		else:
			content = s.GetBinContent(i)
		#~ print "bin %d Content %e"%(i,s.GetBinContent(i) )
		s.SetBinContent( i, log( content ) )
				

	ranges = [( 0.7, 2.1 ), ( 3.4, 7.0 )] 
	

	s.GetYaxis().SetTitle('ln( Eintr#ddot{a}ge )')
	#~ s.SetAxisRange( ranges[1][0] - 0.5, ranges[1][1] + 0.5 )
	fit1 = TF1('tail', 'pol1', ranges[1][0], ranges[1][1] )
	s.Fit('tail','r')
	#~ s.SetStats(1)
	s.Draw()
	
	xmin = 0.75
	xmax = 0.95
	ymin = 0.17
	ymax = 0.74
	
	can.Update()
	
	can.SaveAs("tailFit.pdf")
	
	s2 = subtractfunc (s,fit1,0.0,12)
	fit2 = TF1('peak', 'pol1', ranges[0][0], ranges[0][1] )
	s2.Fit("peak",'r')
	s2.SetStats(0)
	s2.SetMinimum(0)
	s2.Draw()
	
	can.Update()
	
	expfit = TF1('expfit', 'exp([0]+x*[1])', ranges[0][0], ranges[0][1] )
	expfit.SetParameters(fit1.GetParameter(0),fit1.GetParameter(1))
	expfit.SetParError(0,fit1.GetParError(0))
	expfit.SetParError(1,fit1.GetParError(1))
	
	sxmax = 7.0
	
	s3 = subtractfunc(signal,expfit,0.0,sxmax)
	
	#~ for i in range(s3.FindBin(0),s3.FindBin(0)+15):
		#~ print "%d e_b %e  %e"%(i,s3.GetBinError(i),1./s3.Integral()*s3.GetBinError(i))
		#~ print "%signal d e_a %e"%(i,signal.GetBinError(i))
	s3.Scale(1./s3.Integral())
	print"-------------------------------"
	#~ for i in range(s3.FindBin(0),s3.FindBin(0)+15):
		#~ print "%d e_a %e"%(i,s3.GetBinError(i))
	#~ print "test %e %e"%(signal.GetBinContent(142),s3.GetBinContent(142))
	tau_ori , err_tau_ori = centroidShift(signal,background ,signal.FindBin(-1.),signal.FindBin(sxmax))
	tau, err_tau = centroidShift(s3,background ,signal.FindBin(-1.),signal.FindBin(sxmax))

	print "centroid shift (corrected) tau_s:%e +- %e"%(tau,err_tau)
	print "centroid shift (uncorrected) tau_s:%e +- %e"%(tau_ori,err_tau_ori)
	
	can.Update()
	can.SaveAs("peakfit.pdf")
	#~ can.SetLogy()
	#~ s3.SetMinimum(1e-6)
	#~ t1fit = TF1("t1fit" , "expo",0.9,3.0)
	#~ s3.Fit("t1fit","r")
	#~ s3.Draw()
	#~ signal.SetMarkerColor(8)
	background.SetAxisRange(-2.,4,"X")
	background.Scale(1./background.Integral())
	signal.SetAxisRange(-2.,4,"X")
	signal.SetLineWidth(3)
	signal.Scale(1./signal.Integral())
	background.SetLineWidth(3)
	background.Draw("Hist")
	signal.Draw("SAMEHIST")
	
	
	leg = TLegend(0.6, 0.68, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( signal, "%s "%signalname, "l")
	#~ leg.AddEntry( s3, "%s: Signal nur #tau_{1}"%signalname, "P")
	leg.AddEntry( background, "^{60}Co ", "l")
	leg.Draw()
	
	can.SaveAs("centroid_%s.pdf"%signalname)

	can.Close()
	


def globalFit( signal, saveAffix,  ranges = [(0.2, 9.0)] ):
	'''
	uses convolution fit
	signal, background: histograms
	returns: void
	'''
	from ROOT import TF1,TCanvas, gStyle, TLine
	from re import sub
	gStyle.SetStatFontSize(0.09)
	# human readable string for fit
	f1 = 'amp * exp( 1/tau * ( mean - time + sigma**2 / (2 * tau ) ) ) * TMath::Erfc( 1./(sqrt(2) * sigma) * ( mean - sigma**2/tau - time) )'
	# cast human readable sting to machine string
	f1 = sub( 'mean', '[0]', f1 )
	f1 = sub( 'sigma', '[1]', f1 )
	f1 = sub( 'time', 'x', f1 )
	f2 = f1
	f1 = sub( 'tau', '[2]', f1 )
	f1 = sub( 'amp', '[3]', f1 )
	f2 = sub( 'tau', '[4]', f2 )
	f2 = sub( 'amp', '[5]', f2 )
	fitstring = f1+'+'+f2
	defaultRes = signal.Clone()

	for i, ran in enumerate(ranges):
		res = defaultRes.Clone()
		fit = TF1("fit", fitstring, ran[0], ran[1] )
		fit.SetParNames('#mu',"#sigma","#tau_{1}", "A_{1}", "#tau_{2}", "A_{2}" )
		fit.SetParameter( 0, 4.80497e-01)
		fit.SetParameter( 1, 3.70915e-01)
		fit.SetParameter( 2, 4.49595e-01)
		fit.SetParameter( 3, 2.63383e-02)
		fit.SetParameter( 4, 2.00746e+00)
		fit.SetParameter( 5, 1.96099e-03)

		# draw histogram
		can = TCanvas(randomName(), 'globalFit', 1300, 800 )
		can.SetBatch()
		can.Divide(1,2)
		can.cd(1)
		can.SetLogy()
		signal.Fit('fit', "r")

		can.cd(2)
		# compure residuals
		res.SetAxisRange( ran[0], ran[1] )
		for j in range( res.GetXaxis().GetNbins() +1 ):
			res.SetBinContent( j, res.GetBinContent(j) - fit.Eval( res.GetBinCenter(j) ) )
		res.SetYTitle('Residuen')
		res.Draw()
		line = TLine( ran[0], 0,  ran[1], 0 )
		line.Draw()

		can.SaveAs("globalFit{}{}.pdf".format(saveAffix,i))
		print( '{} - {} & {} & {}\\\\'.format( ran[0], ran[1], printError( fit.GetParameter(2), fit.GetParError(2) ), printError( fit.GetParameter(4), fit.GetParError(4) ) ) )
		can.Close()




def centroidShift( signal, background, xmin = 0, xmax  = 16000 ):
	# this function is not working, since it is only valid for small τ
	'''
	centroid shift method, for more information see laboratory manual
	input:
	signal: histogram of signal events (e.g. aluminium )
	background: histogram of background events (e.g. co60 )
		the histogramms should have same settings (nbins, xmin, xmax)
	xmin/xmax: evaluate only a cerain region
	output:
	τ, error  in channel numbers
	'''

	signal.GetXaxis().SetRange( xmin, xmax ) # if integer -> bins, else user-range
	background.GetXaxis().SetRange( xmin, xmax ) # if integer -> bins, else user-range
	t = ( signal.GetMean() - background.GetMean() ) #* signal.GetBinWidth(0)
	from math import sqrt
	s = sqrt ( signal.GetRMS()**2 / ( signal.GetEntries() -1 ) + background.GetRMS()**2 / (background.GetEntries() -1 ) )
	return t, s
	
def subtractfunc (hist , func,xmin,xmax):
	from math import sqrt
	result = hist.Clone()
	for i in range(hist.FindBin(xmin),hist.FindBin(xmax)):
		t = hist.GetBinCenter(i)
		c = func.GetParameter(0) 
		e_c = func.GetParError(0)
		a = func.GetParameter(1)
		e_a = func.GetParError(1)
		f = func.Eval(t)
		e_f = f * sqrt( e_c**2 + t**2 * e_a**2 )
			
		result.SetBinContent( i, hist.GetBinContent(i) - f )
		result.SetBinError(i,sqrt(hist.GetBinError(i)**2 + e_f**2))
			#~ print "t %.1e c %.1e e_c %.1e a %.1e e_a %.1e "%(t,c,e_c,a,e_a)
			#~ print "%d e_befor %e e_after %e func %e e_func %e"%(i,hist.GetBinError(i),result.GetBinError(i),f,e_f)
			#~ print""
	return result

# execute programs
globalFit( polytime, 'poly', [ (0.2,8), (0.9,8), (0.2,9) ] )
globalFit( alutime, 'alu', [ (0.2,7), (0.9,8), (0.2,9) ] )
twoLinearFits( polytime, 'poly', [ ( 0.6, 1.7 ), ( 3.5, 8.0 ) ] )
twoLinearFits( alutime, 'alu', [ (0.6,1.7), (2.9,6) ] )
calculateDeconvolution( poly, co, "Polyethylen", "Cobalt" )
linear_and_centroid(polytime,cotime,"Polyethylen")
linear_and_centroid(alutime,cotime,"Aluminium")
