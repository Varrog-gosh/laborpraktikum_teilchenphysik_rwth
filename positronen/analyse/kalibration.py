#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()
from ROOT import TCanvas, TH1, TF1, TGraphErrors
from sys import exit
from tools import *

loglevel = False

def bufferToSortedList( length, buffer ):
	output = []
	for i in range( length ):
		output.append( buffer[i] )
	return sorted( output )


def peakToArray( filename, minKanal , maxKanal ):
	hist = tkaToHist( filename , minKanal, maxKanal )
	from ROOT import TSpectrum
	from numpy import array
	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.SetLogy()
	can.cd()
	hist.Draw()
	s = TSpectrum( 64 ) #max number of peaks
	npeaks = s.Search( hist, 8, "", 0.005 ) # ( hist, sigma, '', threshold )
	#can.SaveAs('peaksToArray.pdf')
	can.Close()
	peaks = bufferToSortedList( npeaks, s.GetPositionX() )
	distance = 50 # minimal distance between channels
	# clear array of double peaks, which have less than distance channels distance
	for i in range( len(peaks) - 2, -1, -1):
		if peaks[i+1] - peaks[i] <  distance :
			del peaks[i+1]
			npeaks -= 1
	from array import array
	# fit gaus functions
	x = array('d')
	ex = array('d')
	for peak in peaks:
		fit = TF1('fit', 'gaus', peak - distance/3, peak + distance/3)
		fit.SetParameters( hist.GetBinContent( hist.FindBin( peak ) ), peak, 5 )
		hist.Fit('fit', 'rq')
		if peak - fit.GetParameter(1) > 4 and loglevel:
			print 'Zu große abweichung von fit zu peakfinder bei ', peak
		else:
			x.append( fit.GetParameter(1) )
			ex.append( fit.GetParameter(2) ) # use σ for fit, and not error or mean, is this correct?
	valError = [x, ex]
	can.Close()
	return valError

def kalibrationTotalFunction( filename = 'data/kali_montag.TKA', firstpeak = 1 , minKanal = 1900, maxKanal = 0 ):
	x, ex = peakToArray( filename, minKanal, maxKanal )
	y = []
	timestep = 0.5
	for i in range( len(x) ):
		y.append( timestep * (i + firstpeak) )
	ey = [0.075]*len(y)
	import numpy
	# create graph
	y = numpy.array( y, dtype = 'd' )
	ey = numpy.array( ey, dtype = 'd' )
	gr =  TGraphErrors( len(x), x, y, ex, ey )

	# two ararys containing fit parametres
	par1 = numpy.zeros( 3, dtype='d')
	par2 = numpy.zeros( 2, dtype='d')

	# change from one function to another
	cut = 5000

	# two fit functions in certain ranges
	g1 = TF1("g1", "gaus", 1000, cut )
	g2 = TF1("g2", "pol1", cut, 17000 )
	# total fit function
	total = TF1("total", "gaus(0)+pol1(4)", 1000, 17000)
	gr.Fit(g1,"R")
	gr.Fit(g2,"R+")
	g1.GetParameters(par1)
	g2.GetParameters(par2)
	par = numpy.concatenate( (par1, par2) )
	total.SetParameters(par)
	total.SetLineColor(4)
	gr.Fit(total,"R+")
	gr.Draw("ap")
	raw_input()
kalibrationTotalFunction( )


def kalibration_nonlin (filename, firstpeak, minKanal = 0, maxKanal = 0):
	y, ey = peakToArray( filename, minKanal, maxKanal )
	from array import array
	from ROOT import TPaveStats,gStyle,TPaveText,TFitResultPtr,TPad,TLine


	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.cd()
	gStyle.SetOptFit(0)

	hPad = TPad("fitPad", "Fit", 0, 0.3, 1, 1)
	hPad.SetFillStyle(4000)
	hPad.SetBorderSize(0)
	hPad.Draw()
	hPad.cd()

	# border where to change functions
	cut = 5000


	x = array('d')
	ex = array ('d')
	timestep = 0.5
	for i in range( len(y) ):
		x.append( timestep * (i + firstpeak) )
		ex.append(0.075)
	#~ graph = TGraphErrors(len(y),x,y,ex,ey)
	graph = TGraphErrors(len(y),y,x,ey,ex)
	graph.GetXaxis().SetTitle("Kanal")
	graph.GetYaxis().SetTitle("t [ns]")
	graph.Draw("AP")
	# f1 = TF1("f1","[0]+[1]*x**2",1900, cut + 103); # changed to linear function
	f1 = TF1("f1","pol1",1900, cut + 103)
	f1.SetParName(0,"A")
	f1.SetParName(1,"B")
	f1.SetLineWidth(2)

	result1 = graph.Fit(f1,"RSq")
	if loglevel:
		result1.Print("V")
	chi2ndf1 = f1.GetChisquare() / f1.GetNDF()
	if loglevel:
		print ("chi^2/ndf %e ")%chi2ndf1

	textf1 = TPaveText(0.23,0.32,0.35,0.5,"NDC")
	textf1.AddText("A + B x   (2000 < x < %s)"%cut)
	textf1.AddText("A: %.4f #pm %.4f"%(f1.GetParameter(0),f1.GetParError(0)))
	textf1.AddText("B: %.2e #pm %.2e"%(f1.GetParameter(1),f1.GetParError(1)))
	textf1.AddText("#frac{#chi^{2}}{NDF}: %.4f"%chi2ndf1)
	textf1.SetFillColor(0)
	textf1.SetTextSize(0.03)
	#~ textf1.SetBorderSize(1)
	
	textf1.Draw("same")

	f2 = TF1("f2","[0]+x*[1]", cut, 17000)
	f2.SetParName(0,"C")
	f2.SetParName(1,"D")
	f2.SetLineWidth(2)
	graph.Fit(f2,"R+q")
	
	chi2ndf2 = f2.GetChisquare() / f2.GetNDF()
	if loglevel:
		print ("chi^2/ndf %e")%(f2.GetChisquare() / f2.GetNDF())
	
	textf2 = TPaveText(0.63,0.32,0.72,0.5,"NDC")
	textf2.AddText("C + D x   (%s < x < 16000)"%cut)
	textf2.AddText("C: %.4f #pm %.4f"%(f2.GetParameter(0),f2.GetParError(0)))
	textf2.AddText("D: %.2e #pm %.2e"%(f2.GetParameter(1),f2.GetParError(1)))
	textf2.AddText("#frac{#chi^{2}}{NDF}: %.4f"%chi2ndf2)
	textf2.SetFillColor(0)
	textf2.SetTextSize(0.03)

	textf2.Draw("same")
	can.cd()
	
	residualPad = TPad("resPad", "Residuals", 0, 0, 1, 0.3)
	residualPad.SetFillStyle(4000)
	residualPad.SetFrameFillStyle(4000)
	residualPad.SetBorderSize(0)
	residualPad.Draw()
	residualPad.cd()

	residuals = array('d')
	for i in range(len(y)):
		for func in [f1,f2]:
			if func.GetXmin() < y[i] and y[i] < func.GetXmax():
				residuals.append( x[i] - func.Eval(y[i]) )
	if loglevel:
		print residuals [0]
		print y [0]
	resgraph = TGraphErrors( len(residuals)-1, y, residuals, ey, ex )
	resgraph.Draw("ap")
	resgraph.GetXaxis().SetLabelSize(0.09)
	resgraph.GetYaxis().SetLabelSize(0.09)
	resgraph.GetYaxis().SetNdivisions(4,1)
	line = TLine( resgraph.GetXaxis().GetXmin(), 0, resgraph.GetXaxis().GetXmax(), 0 )
	line.SetLineColor(2)
	line.SetLineStyle(2)
	line.Draw()
	dif = f1.Eval( cut )-f2.Eval( cut )
	#~ raw_input()
	if loglevel:
		print "difference between function at: %f"%dif

	can.SaveAs('kalibration_nonlin.pdf')
	residualPad.Close()
	hPad.Close()
	can.Close()
	return [f1,f2]


def tkaToTimeHist( filename , funcs, xmin_time,xmax_time,rebin ): #nBins, xMin, xMax,
	'''
	not used now, and will never be used
	'''
	import tools
	
	#~ data = tools.readFile( filename )[0]
	#~ length = len( data )
	#~ hist = TH1('', ";Kanalnummer;Eintr#\"age", nBins, xMin, xMax )	
	hist = tkaToHist(filename)
	nBins = hist.GetNbinsX()
	hist_time = TH1F('', ";Zeit[ns];Eintr#\"age", nBins, xmin_time, xmax_time )
	histlist =[]
	if loglevel:
		print "xmin: %f xmax: %f "%(funcs[0].GetXmin() , funcs[0].GetXmax() )
		print "xmin: %f xmax: %f "%(funcs[1].GetXmin() , funcs[1].GetXmax() )
	for func in funcs:
		for i in range (nBins):
			if hist.GetBinLowEdge(i) > func.GetXmin() and hist.GetBinLowEdge(i)+ hist.GetBinWidth(i) < func.GetXmax():
				time_bin = hist_time.FindBin(  func.Eval( hist.GetBinCenter(i))  )
				histlist.append([time_bin,hist.GetBinContent(i)])
	
	sumval = 0
	final_histlist =[]
	#~ print histlist
	for i in range(len(histlist)):
		if i < len(histlist)-1:
			tbin1 = histlist[i][0]
			val1	 = histlist[i][1]
			tbin2 = histlist[i+1][0]
			val2	 = histlist[i+1][1]
			
			if abs(tbin1 - tbin2) < 0.0001:
				sumval+=val1
			else:
				if sumval > 0.0:
					final_histlist.append([tbin1,sumval])
				else:
					final_histlist.append([tbin1,val1])
				sumval = 0
	
	for entry in final_histlist:
		hist_time.SetBinContent(  entry[0] ,entry[1] )
	if rebin > 0.01:
		hist_time.Rebin(rebin)
	return hist_time


def tkaToTimeHist_knut( filename , funcs, xmin_time,xmax_time,rebin ): #nBins, xMin, xMax,
	'''
	not used now, and will never be used
	'''
	import tools
	can = TCanvas()
	can.cd()
	# asume two linear functions
	# otherwise a numerical solver is of use to find the interception point
	cut = ( funcs[0].GetParameter(0) - funcs[1].GetParameter(0) ) / ( funcs[1].GetParameter(1) - funcs[0].GetParameter(1) )
	#cutbin = hist.FindBin( cut )
	hist1 = tkaToHist(filename, 0, int(cut) )
	hist2 = tkaToHist( filename, int(cut)+1, 0)
	hist1.Draw()
	hist2.Draw("same")
	raw_input()
	can.Close()
	exit()
	nBins = hist.GetNbinsX()
	hist_time = TH1('', ";Zeit[ns];Eintr#\"age", nBins, xmin_time, xmax_time )
	histlist =[]

	a->Set(a->GetNbins(),
	        Scale(a->GetXmin()), // new Xmin
	        Scale(a->GetXmax())); // new Xmaxa->Set(a->GetNbins(),
	        Scale(a->GetXmin()), // new Xmin
	        Scale(a->GetXmax())); // new Xmax
	for i in range( cutbin ):
		a = hist.GetXaxis()
		import pdb; pdb.set_trace()

		hist_time.SetBinContent(i,3)
		if hist.GetBinLowEdge(i) > func.GetXmin() and hist.GetBinLowEdge(i)+ hist.GetBinWidth(i) < func.GetXmax():
				time_bin = hist_time.FindBin(  func.Eval( hist.GetBinCenter(i))  )
				histlist.append([time_bin,hist.GetBinContent(i)])
	
	sumval = 0
	final_histlist =[]
	#~ print histlist
	for i in range(len(histlist)):
		if i < len(histlist)-1:
			tbin1 = histlist[i][0]
			val1	 = histlist[i][1]
			tbin2 = histlist[i+1][0]
			val2	 = histlist[i+1][1]
			
			if abs(tbin1 - tbin2) < 0.0001:
				sumval+=val1
			else:
				if sumval > 0.0:
					final_histlist.append([tbin1,sumval])
				else:
					final_histlist.append([tbin1,val1])
				sumval = 0
	
	for entry in final_histlist:
		hist_time.SetBinContent(  entry[0] ,entry[1] )
	if rebin > 0.01:
		hist_time.Rebin(rebin)
	return hist_time


def PlotHist(hist,title,xtitle,logmode = "0"):
	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.cd()
	if logmode == 1:
		can.SetLogy()
	hist.SetTitle(title)
	hist.GetXaxis().SetTitle(xtitle)
	hist.GetYaxis().SetTitle("Eintr#ddot{a}ge")
	hist.Draw()
	
	can.SaveAs('hist_%s.pdf'%title)
	can.Close()

#fu = kalibration_nonlin('data/kali_montag.TKA', 1, 1000 ) # number of first peak ( x%in = 2000 -> firstpeak = 1 )


#time_hist = tkaToTimeHist_knut( "data/aluminium.TKA" , fu,0,12,2)
#time_hist.Draw()
#hist = tkaToHist("data/aluminium.TKA",2000,16000)
#PlotHist(hist,"Alu_channnel","channel")
#PlotHist(time_hist,"Alu_time","t[ns]",0)
