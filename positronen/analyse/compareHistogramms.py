#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
from tools import *
from Styles import tdrStyle
from kalibration import *
tdrStyle()

def normedHist( name, color, func = 0):
	if func == 0:
		hist,time = tkaToHist( name, 2000, 16000 ,True)
		hist.Rebin(50)
	else:
		hist = tkaToTimeHist(name, func , -2, 8 )
	hist.Scale(1./hist.Integral())
	hist.GetYaxis().SetTitle("Normierte Eintr#ddot{a}ge")
	hist.SetLineColor( color )
	return hist

def timenormedHist( name, color, func = 0):
	if func == 0:
		hist,time = tkaToHist( name, 2000, 16000 ,True)
		hist.Rebin(50)
	else:
		hist,time = tkaToTimeHist(name, func , -2, 8,True )
	hist.Scale(1./time)
	hist.GetYaxis().SetTitle("Normierte Eintr#ddot{a}ge")
	hist.SetLineColor( color )
	hist.SetMarkerStyle( 23 + color )
	hist.SetMarkerSize( 1.5 )
	hist.SetMarkerColor( color )
	return hist
	

func = kalibration()
alu = normedHist( 'data/aluminium.TKA', 2 )
poly = normedHist( 'data/poly.TKA', 4 )

alutime = normedHist( 'data/aluminium.TKA', 2, func )
polytime = normedHist( 'data/poly.TKA', 4, func )

co = normedHist( 'data/co60.TKA', 1 )
co2 = normedHist( 'data/co60_2.TKA', 12 )

cotime = normedHist( 'data/co60.TKA', 1, func )
co2time = normedHist( 'data/co60_2.TKA', 12 , func )

alu_timenormed = timenormedHist( 'data/aluminium.TKA', 2, 0 )
poly_timenormed = timenormedHist( 'data/poly.TKA', 4, 0 )
co_timenormed = timenormedHist( 'data/co60.TKA', 1, 0 )
co2_timenormed = timenormedHist( 'data/co60_2.TKA', 1, 0 )

def compareHistos( signal, background, signalname, backgroundname, save ):
	'''
	plots two histos and save the result as pdf
	'''
	from ROOT import TH1F,TSpectrum, TLegend, TCanvas

	can = TCanvas(randomName(), 'comparison', 1400, 800 )
	can.cd()
	can.SetBatch()
	can.SetLogy()
	for h in signal, background:
		h.SetLineWidth(2)
	signal.Draw("e, hist")
	background.Draw("e, hist,same")

	leg = TLegend(0.6, 0.7, 1,1)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( signal, signalname, "l")
	leg.AddEntry( background, backgroundname, "l")
	leg.Draw()
	print 'Histogramme statistisch vereinbar mit ', signal.Chi2Test( background, 'uu,norm')
	can.SaveAs( save )
	can.Close()

def compareCo( co1, co2 ,isTime = False):
	import ROOT
	from ROOT import TCanvas, TLegend,TSpectrum,TPaveStats
	can = TCanvas("canvas")
	can.cd()
	#~ can.SetBatch()
	can.SetCanvasSize( 1300, 800 )
	#~ can.SetLogy()
	co1.SetFillStyle(3003)
	co1.SetFillColor(ROOT.kCyan+2)
	co1.SetLineColor(ROOT.kCyan+2)
	co1.SetAxisRange(2200,8000,"X")
	co1.Draw("HISTF")

	bgxmin = 6000
	bgxmax = 14000

	s = TSpectrum( 1 )
	npeaks = s.Search( co1, 8, "same", 1e-4 ) # ( hist, sigma, 'drawoption', threshold )
	peaks = bufferToSortedList( npeaks, s.GetPositionX() )
	
	if isTime:
		peakminus = 1.5
		peakplus = 0.5
	else:
		peakminus = 1500
		peakplus = 500
		
	print "npeaks %d"%len(peaks)
	fit1 = TF1('fit1', 'gaus', peaks[0]-peakminus, peaks[0]+peakplus)
	co1.Fit("fit1","R0")
	fit1.SetLineColor(ROOT.kCyan)
	fit1.SetLineWidth(3)
	co1.SetAxisRange(3000,8000,"X")
	fit1.Draw("same")
	bg_integral1 = co1.Integral(co1.FindBin(bgxmin),co1.FindBin(bgxmax))
	xmin = 0.75
	xmax = 0.95
	ymin = 0.17
	ymax = 0.74
	can.Update()
	p1 = TPaveStats(co1.GetListOfFunctions().FindObject("stats"))	
	#~ co1.GetListOfFunctions().Remove(p1);
	co1.SetStats(0)
	p1.SetX1NDC(xmin)
	p1.SetX2NDC(xmax)
	p1.SetY1NDC(ymin)
	p1.SetY2NDC(ymax)
	p1.SetFillColor(0)
	p1.SetTextSize(0.03)
	p1.SetTextAlign(12)


	co2.SetFillStyle(3003)
	co2.SetFillColor(ROOT.kBlue+2)
	co2.SetLineColor(ROOT.kBlue+2)
	co2.Draw("sameHIST")

	npeaks = s.Search( co2, 8, "same", 1e-4 ) # ( hist, sigma, 'drawoption', threshold )
	peaks = bufferToSortedList(npeaks,s.GetPositionX())
	print "number of peaks %d"%len(peaks)
	fit2 = TF1('fit2', 'gaus', peaks[0] - peakminus, peaks[0] + peakplus)
	co2.Fit("fit2","R0+")
	bg_integral2 = co2.Integral(co2.FindBin(bgxmin),co2.FindBin(bgxmax))
	
	p1.AddText("Ergebnisse")
	p1.AddText("Vor der Messung:")
	p1.AddText("#chi^{2}/NDF : %.3f"%(fit1.GetChisquare() / fit1.GetNDF()))
	p1.AddText("Constant: %.1e#pm%.0e"%(fit1.GetParameter(0),fit1.GetParError(0)))
	p1.AddText("#mu_{1}: %.1f#pm%.1f"%(fit1.GetParameter(1),fit1.GetParError(1)))
	p1.AddText("#sigma_{1}: %.1f#pm%.1f"%(fit1.GetParameter(2),fit1.GetParError(2)))
	p1.AddText("")
	p1.AddText("Nach der Messung:")
	p1.AddText("#chi^{2}/NDF : %.3f"%(fit2.GetChisquare() / fit2.GetNDF()))
	p1.AddText("Constant: %.1e#pm%.0e"%(fit2.GetParameter(0),fit2.GetParError(0)))
	p1.AddText("#mu_{2}: %.1f#pm%.1f"%(fit2.GetParameter(1),fit2.GetParError(1)))
	p1.AddText("#sigma_{2}: %.1f#pm%.1f"%(fit2.GetParameter(2),fit2.GetParError(2)))
	p1.AddText("")
	p1.AddText("#Delta#mu: %.1f"%(fit1.GetParameter(1) - fit2.GetParameter(1)))
	p1.AddText("")
	p1.AddText("#mu_{mean} : %.1f" %((fit1.GetParameter(1) + fit2.GetParameter(1))/2))
	p1.AddText("#sigma_{mean} : %.1f" %((fit1.GetParameter(2) + fit2.GetParameter(2))/2))
	p1.AddText("")

	fit2.SetLineColor(ROOT.kBlue)
	fit2.SetLineWidth(3)
	fit2.Draw("same")
	p1.Draw();
	
	leg = TLegend(0.7, 0.78, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( co1, "^{60}Co vor Messung", "f")
	leg.AddEntry( co2, "^{60}Co nach Messung", "f")
	leg.Draw()
	
	print "******  Background estimation: ****** \n "
	print co1.FindBin(bgxmin)
	print co1.FindBin(bgxmax)
	print "Range Channel %d to %d"%(bgxmin,bgxmax)
	bg1 = bg_integral1 / abs(bgxmin-bgxmax)
	bg2 = bg_integral2/ abs(bgxmin-bgxmax)
	print "Co1 %f events %e Events / channel"%(bg_integral1,bg1)
	print "Co2 %f events %e Events / channel"%(bg_integral2,bg2)
	print "Mean %e Events / channel"%(float((bg1+bg2)/2))
	can.SaveAs('compareCo.pdf')
	can.Close()



# execute programs
# compareHistos( alu, co , "Aluminium", "Cobalt", "signal+background.pdf")
#~ compareHistos( polytime , alutime,  "Polytehylen", "Aluminium", "signal+signal.pdf")

compareCo( co, co2,False )
#~ compareCo( co_timenormed, co2_timenormed,False )
