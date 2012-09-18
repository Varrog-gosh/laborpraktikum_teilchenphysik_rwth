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
		hist = tkaToTimeHist(name, func , -2, 8 )
	hist.Scale(1./hist.Integral())
	hist.GetYaxis().SetTitle("Normierte Eintr#ddot{a}ge")
	hist.SetLineColor( color )
	hist.SetMarkerStyle( 23 + color )
	hist.SetMarkerSize( 1.5 )
	hist.SetMarkerColor( color )
	return hist


func = kalibration()
alutime = normedHist( 'data/aluminium.TKA', 2, func )
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
	τ in chanel numbers is printed
	a root file is created to save cpu work
	'''
	from ROOT import TH1D,TSpectrum, TF1,TCanvas,TLegend

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
	d.Draw("sameLhist")

	leg = TLegend(0.6, 0.7, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( signal, signalname, "lp")
	leg.AddEntry( background, backgroundname, "lp")
	leg.AddEntry( d, "Entfaltung des Spektrums", "l")
	leg.Draw()

	can.SaveAs("deconvolution.pdf")
	return d
##poly = normedHist( 'data/poly.TKA', 4 )
##co = normedHist( 'data/co60.TKA', 1 )
#calculateDeconvolution( polytime, cotime, "Polyethylen", "Cobalt" )



def twoLinearFits( signal, ranges):
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
		signal.SetBinContent( i, log( signal.GetBinContent(i) ) )

	for i, ran in enumerate( ranges ):
		can = TCanvas( 'linear', "dualliniar", 700, 800 )
		can.SetBatch()
		can.Divide(1,2)
		can.cd(1)

		s = signal.Clone()
		s.GetYaxis().SetTitle('ln( Eintr#ddot{a}ge )')
		s.SetAxisRange( ran[0] - 0.5, ran[1] + 0.5 )
		fit = TF1('mypol1', 'pol1', ran[0], ran[1] )
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
		info.AddText( '#tau = ' + sub('±', "#pm", printError(-1/func.GetParameter(1), func.GetParError(1)/(func.GetParameter(1))**2, 'ns')))
		info.Draw()

		# Compute and draw residuals, not working now
		can.cd(2)
		res = signal.Clone()
		res.SetAxisRange( ran[0], ran[1] )
		for j in range( res.GetXaxis().GetNbins() +1 ):
			res.SetBinContent( j, res.GetBinContent(j) - func.Eval( res.GetBinCenter(j) ) )
		res.Draw()
		line = TLine( ran[0], 0,  ran[1] ,0)
		line.Draw()

		can.SaveAs('linearFit{}.pdf'.format(i))
		can.Close()



def globalFit( signal, background ):
	'''
	uses convolution fit
	signal, background: histograms
	returns: void
	'''
	from ROOT import TF1
	gaus = TF1('mygaus', 'gaus', -2, 0.3 )

	background.Fit('mygaus', 'r')
	mean = background.GetFunction('mygaus').GetParameter(1)
	sigma = background.GetFunction('mygaus').GetParameter(2)

	from re import sub
	#par: [mean, sigma, tau1, a1, tau2, a2 ]
	#num: [ 0  , 1    , 2   , 3 , 4   , 5  ]
	f1 = 'a * 1./( 2*tau) * exp( 2/tau * ( mean - time + sigma**2 / tau ) ) * TMath::Erfc( 1./(sqrt(2) * sigma) * ( mean - 2*sigma**2/tau - time) )'
	f1 = sub( 'mean', '[0]', f1 )
	f1 = sub( 'signa', '[1]', f1 )
	f2 = f1
	f1 = sub( 'a', '[2]', f1 )
	f1 = sub( 'tau', '[3]', f1 )
	f2 = sub( 'a', '[2]', f2 )
	f2 = sub( 'tau', '[3]', f2 )
	print f1
	print f2


	fit = TF1('myfit', ' [3] * (2*[2]) * exp(2/[2] * ( [1] - x + [2]**2/[0] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[0] - x ) )+ [4]/(2*[5]) * exp(2/[5] * ( [1] - x + [2]**2/[5] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[5] - x ) )' , -2, 6 )
	#fit = TF1('myfit', '[3]/(2*[0]) * exp(2/[0] * ( [1] - x + [2]**2/[0] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[0] - x ) )' , -2, 6 )
	#fit2 = TF1("fit","myfit(0)+myfit(4)",2000,4000)

	fit.SetParameter( 1, mean)
	fit.SetParameter( 2, sigma )
	fit.SetParameter(0, 1.9)
	fit.SetParameter(3, 0.03)
	fit.SetParameter(4, 0.03)
	fit.SetParameter(5, 0.3)
	#signal.Draw()
	#~ fit.Draw("same")
	signal.Fit('myfit')
	raw_input()

#~ globalFit( polytime, cotime )


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
	t = ( signal.GetMean() - background.GetMean() ) * signal.GetBinWidth(0)
	from math import sqrt
	s = sqrt ( signal.GetRMS()**2 / ( signal.GetEntries() -1 ) + background.GetRMS()**2 / (background.GetEntries() -1 ) )
	return t, s

# execute programs
#twoLinearFits( polytime, [ ( 0.7, 1.8 ), ( 3.4, 7.0 ) ] )
calculateDeconvolution( poly, co, "Poly", "Co" )
