#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
from tools import *
from ROOT import *
from ROOT import TSpectrum
from Styles import tdrStyle
from array import array
from kalibration import *
#from kalibration import fu
#from kalibration import tkaToTimeHist
tdrStyle()
from sys import exit

#tkaToTimeHist("data/aluminium.TKA", fu, 0, 12,2).Draw()



def globalFit( signal, background ):
	# not working now
	background.Fit('gaus') # fit doesnot seem to care about normalization
	# perhaps comment SetNormFactor()
	mean = background.GetFunction('gaus').GetParameter(1)
	sigma = background.GetFunction('gaus').GetParameter(2)

	from ROOT import TF1
	# par : [tau, mu, sigma,const]
	fit = TF1('myfit', '[3]/(2*[0]) * exp(2/[0] * ( [1] - x + [2]**2/[0] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[0] - x ) )' , 2000, 16000 )
	fit2 = TF1("fit","myfit(0)+myfit(4)",2000,4000)
	fit.FixParameter( 1, mean)
	fit.FixParameter( 2, sigma )
	fit.SetParameter(0, 1500)
	signal.Draw()
	#~ fit.Draw("same")
	signal.Fit('fit')
	raw_input()



def normedHist( name, color ,isTime = False):
	
	if isTime:
		func = kalibration( )
		hist = tkaToTimeHist(name, func , -2, 8 )
	else:
		hist = tkaToHist( name, 2000, 16000,False )
		hist.Sumw2()
		hist.Rebin(50)
	hist.Scale(1./hist.Integral())
	hist.SetLineColor( color )
	return hist

def timenormedHist( name, color ):
	hist,time = tkaToHist( name, 2000, 16000,True )
	hist.Sumw2()
	hist.Rebin(50)
	hist.Scale(1./time)
	hist.SetLineColor( color )
	return hist
	


alu = normedHist( 'data/aluminium.TKA' , 2)
poly = normedHist( 'data/poly.TKA' , 4)

alutime = normedHist( 'data/aluminium.TKA' , 2,True)
polytime = normedHist( 'data/poly.TKA' , 4,True)

co = normedHist( 'data/co60.TKA', 1 )
co2 = normedHist( 'data/co60_2.TKA', 12 ,)

cotime = normedHist( 'data/co60.TKA', 1,True )
co2time = normedHist( 'data/co60_2.TKA', 12 ,True)


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

def safeHist (hist, filename ):
	outputfile=TFile( filename, "RECREATE")
	hist.Write()
	outputfile.Close()

def calculateDeconvolution( signal, background ):
	'''
	using roots deconvolution class
	τ in chanel numbers is printed
	a root file is created to save cpu work
	'''
	from ROOT import TH1D,TSpectrum, TF1,TCanvas
	
	can = TCanvas()
	can.cd()
	can.SetBatch()
	can.SetCanvasSize( 1300, 800 )
	can.SetLogy()
	#~ can.Divide(1,2)
	#~ can.cd(1)
	source = histToArray( signal )
	response = histToArray( background )
	s = TSpectrum();
	# parameters for deconvolution:
	# iterations = 1: more iterations -> stange peaks and more noice
	# repetitions =  1: same as above
	# boosting factor = 1: not needed
	s.Deconvolution(source, response, len( source ), 2, 1, 0 )
	
	signal.SetMarkerColor(kMagenta-3)
	signal.SetLineColor(1)
	#~ signal.GetXaxis().SetRangeUser(2500,14000)
	signal.SetMinimum(1e-6)
	signal.Draw("P")
	

	background.SetMarkerColor(kGreen+3)
	background.SetMarkerStyle(34)
	background.Draw("sameP")

	#~ d = TH1D('', 'Kanalnummer;Eintr#ddot{a}ege', len(source), 2000,16000 )
	d = signal.Clone()
	d.SetLineColor(4)
	
	for i in range( len(source) ):
		d.SetBinContent(i + 1,source[i])
	#safeHist( d, 'deconvolution100.root' )
	d.Draw("sameLhist")
	
	leg = TLegend(0.6, 0.7, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( signal, "Signal", "p")
	leg.AddEntry( background, "response", "p")
	leg.AddEntry( d, "Deconvoluted Spectrum", "l")
	leg.Draw()
	

	can.SaveAs("deconvolution.pdf")
	#~ raw_input()
	return d
	

def FitTau(hist,background,isTime = False):
	from ROOT import TH1D, TF1,TCanvas

	# not working now
	background.Fit('gaus') # fit doesnot seem to care about normalization
	# perhaps comment SetNormFactor()
	mean = background.GetFunction('gaus').GetParameter(1)
	sigma = background.GetFunction('gaus').GetParameter(2)

	can = TCanvas("canvastau")
	can.cd()
	#~ can.SetBatch()
	can.SetCanvasSize( 1300, 800 )
	can.SetLogy()
	if isTime:
		fitRanges = [ (-2, 6.5),(3, 6.5)]
	else:
		fitRanges = [ (5000, 6500),(8000, 11000)]
	fit = TF1('fit', 'expo',fitRanges[1][0], fitRanges[1][1] )
	if isTime:
		hist.SetAxisRange(-2,8,"X")
	else:	
		hist.SetAxisRange(4780,14000,"X")
	hist.SetLineColor(4)
	hist.SetMaximum(1)
	hist.Draw("histC")
	fit.SetLineWidth(3)
	fit.SetLineColor(6)
	hist.Fit("fit","r")
	# par : [tau, mu, sigma,const]
	fit2 = TF1('fit2', '[3]/(2*[0]) * exp(2/[0] * ( [1] - x + [2]**2/[0] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[0] - x ) ) + [5]/(2*[4]) * exp(2/[4] * ( [1] - x + [2]**2/[4] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[4] - x ) )' ,fitRanges[0][0],fitRanges[0][1] )
	#~ fit2 = TF1('fit2', 'expo(0)+expo(2)',fitRanges[0][0], fitRanges[0][1] )
	
	fit2.FixParameter(0,-1./fit.GetParameter(1))
	fit2.FixParameter(1,mean)
	fit2.FixParameter(2,sigma)
	fit2.FixParameter(3,fit.GetParameter(0))
	fit2.SetParameter(4,1.5)
	hist.Fit("fit2","r+")
	hist.SetStats(0)
	
	leg = TLegend(0.5, 0.5, .88,1.0,"NDC")
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.SetTextSize(0.03)
	leg.AddEntry( fit2, "Fit 1", "l")
	leg.AddEntry(0,"X(t|c_{i},#tau_{i}) = #frac{C_{i}}{2#tau_{i}} e^{#frac{2}{#tau}(#mu-t+#frac{#sigma^{2}}{#tau_{i}})} Erfc(#frac{1}{#sqrt{2}#sigma}(#mu-#frac{2#sigma^{2}}{#tau_{i}}-t))","")
	leg.AddEntry(0,"Function : X(t|c_{1},#tau_{1})+X(t|c_{2},#tau_{2})+","")
	leg.AddEntry( fit, "Fit 2", "l")
	leg.AddEntry(0,"Function : C_{2} e^{#frac{t}{-#tau_{2}}}","")
	leg.AddEntry(0,"C_{2}: %.4f #pm %.4f"%(fit.GetParameter(0),fit	.GetParError(0)),"")
	leg.AddEntry(0,"#tau_{2}: %.4f #pm %.4f"%(1/fit.GetParameter(1),fit.GetParError(1)),"")
	leg.AddEntry(0,"#chi^{2}/ NDF: %.4f "%(1/fit.GetChisquare()/fit.GetNDF()),"")
	#~ 
	leg.Draw()
	can.Update()

	
	can.SaveAs("taufit.pdf")
	raw_input()

def centroidShift( signal, background, xmin = 0, xmax  = 16000 ):
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

def substractHist(spec,back):
	nbins = back.GetNbinsX()
	sig = spec.Clone()
	for i in range(1,nbins):
		sig.SetBinContent(i,spec.GetBinContent(i)-back.GetBinContent(i))
	return sig


def safeHist (hist):
	outputfile=TFile("spec.root","RECREATE")
	hist.Write()
	outputfile.Close()

def substractHist(spec,back):
	nbins = back.GetNbinsX()
	sig = spec.Clone()
	for i in range(1,nbins):
		sig.SetBinContent(i,spec.GetBinContent(i)-back.GetBinContent(i))
	return sig

def safeHist (hist):
	outputfile=TFile("spec.root","RECREATE")
	hist.Write()
	outputfile.Close()

def plotDataAndBackground( signal, background):
	'''
	only plot tool
	'''
	from ROOT import TH1F,TSpectrum, TLegend, TCanvas

	can = TCanvas()
	can.cd()
	can.SetBatch()
	can.SetCanvasSize( 1300, 800 )
	can.SetLogy()
	signal.Draw()
	background.Draw("same")

	leg = TLegend(0.6, 0.7, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( alu, "Aluminium", "l")
	leg.AddEntry( background, "Cobalt", "l")
	leg.Draw()

	can.SaveAs('firstComparison.pdf')

def compareSignalHistos( alu, poly ):
	from ROOT import TCanvas, TLegend
	can = TCanvas("can1")
	can.cd()
	can.SetBatch()
	can.SetCanvasSize( 1300, 800 )
	can.SetLogy()
	poly.Draw()
	alu.Draw("same")

	leg = TLegend(0.6, 0.7, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( alu, "Aluminium", "l")
	leg.AddEntry( poly, "Polyethylen", "l")
	leg.Draw()
	#print alu.KolmogorovTest( poly, "ND" )
	print alu.Chi2Test( poly , 'p')
	#print poly.KolmogorovTest( alu )
	raw_input()
	can.SaveAs('compareHistos.pdf')
	can.Close()

def compareCo( co1, co2 ,isTime = False):
	from ROOT import TCanvas, TLegend,TSpectrum,TPaveStats
	can = TCanvas("canvas")
	can.cd()
	#~ can.SetBatch()
	can.SetCanvasSize( 1300, 800 )
	#~ can.SetLogy()
	co1.SetFillStyle(3004)
	co1.SetFillColor(kRed)
	co1.Draw("HISTLF")

	bgxmin = 6000
	bgxmax = 14000

	leg = TLegend(0.6, 0.7, .95,.95)
	leg.SetFillColor(0)
	leg.SetLineWidth(0)
	leg.AddEntry( alu, "^{60}Co first", "l")
	leg.AddEntry( poly, "^{60}Co last", "l")
	leg.Draw()
	raw_input()
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
	fit1.Draw("same")
	bg_integral1 = co1.Integral(co1.FindBin(bgxmin),co1.FindBin(bgxmax))
	xmin = 0.55
	xmax = 0.8
	ymin = 0.45
	ymax = 0.95
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


	co2.SetFillStyle(3003)
	co2.SetFillColor(kBlue-6)
	co2.Draw("sameHIST")

	npeaks = s.Search( co2, 8, "same", 1e-4 ) # ( hist, sigma, 'drawoption', threshold )
	peaks = bufferToSortedList(npeaks,s.GetPositionX())
	fit2 = TF1('fit2', 'gaus', peaks[0] - peakminus, peaks[0] + peakplus)
	co2.Fit("fit2","R0+")
	bg_integral2 = co2.Integral(co2.FindBin(bgxmin),co2.FindBin(bgxmax))
	
	p1.AddText("First Peak:")
	p1.AddText("#chi^{2}/NDF : %e"%(fit1.GetChisquare() / fit1.GetNDF()))
	p1.AddText("Constant: %e"%fit1.GetParameter(0))
	p1.AddText("#mu_{1}: %e"%fit1.GetParameter(1))
	p1.AddText("#sigma_{1}: %e"%fit1.GetParameter(2))
	p1.AddText("")
	p1.AddText("Second Peak:")
	p1.AddText("#chi^{2}/NDF : %e"%(fit2.GetChisquare() / fit2.GetNDF()))
	p1.AddText("Constant: %e"%fit2.GetParameter(0))
	p1.AddText("#mu_{2}: %e"%fit2.GetParameter(1))
	p1.AddText("#sigma_{2}: %e"%fit2.GetParameter(2))
	p1.AddText("")
	p1.AddText("#Delta#mu: %f"%(fit1.GetParameter(1) - fit2.GetParameter(1)))
	p1.AddText("")
	p1.AddText("#mu_{mean} : %f" %((fit1.GetParameter(1) + fit2.GetParameter(1))/2))

	fit2.Draw("same")
	p1.Draw();
	
	print "******  Background estimation: ****** \n "
	print co1.FindBin(bgxmin)
	print co1.FindBin(bgxmax)
	print "Range Channel %d to %d"%(bgxmin,bgxmax)
	bg1 = bg_integral1 / abs(bgxmin-bgxmax)
	bg2 = bg_integral1/ abs(bgxmin-bgxmax)
	print "Co1 %f events %f Events / channel"%(bg_integral1,bg1)
	print "Co2 %f events %f Events / channel"%(bg_integral2,bg2)
	print "Mean %f Events / channel"%(float((bg1+bg2)/2))
	can.SaveAs('compareCo.pdf')
	can.Close()
	raw_input()

#globalFit( alu, co2 )


# execute programs
#~ FitTau(alutime,cotime,True)
#~ FitTau(calculateDeconvolution( alutime, cotime ))
#plotDataAndBackground( alu, co )
#print centroidShift( alu, co, 2000, 16000)
#~ compareCo( cotime, co2time,True )
compareCo( co, co2 )
#~ compareSignalHistos( alutime, polytime )
