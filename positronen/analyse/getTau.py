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
	hist.GetYaxis().SetTitle("Normirte Eintr#ddot{a}ge")
	hist.SetLineColor( color )
	hist.SetMarkerStyle( 22 + color )
	hist.SetMarkerSize( 1.5 )
	hist.SetMarkerColor( color )
	return hist


func = kalibration()
alutime = normedHist( 'data/aluminium.TKA', 2, func )
polytime = normedHist( 'data/poly.TKA', 4, func )
cotime = normedHist( 'data/co60.TKA', 1, func )
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


def FitTau(hist,background,isTime = False):
	from ROOT import TH1D, TF1,TCanvas, TLegend

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


def twoLinearFits( signal ):
	from ROOT import TF1, TCanvas, TLegend, 

	can = TCanvas( randomName(), "dualliniar", 1300, 800 )
	can.cd()
	#can.SetBatch()
	signal.Draw()
	raw_input()
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
twoLinearFits( polytime )


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

	# par : [tau, mu, sigma,const]
	fit = TF1('myfit', '[3]/(2*[0]) * exp(2/[0] * ( [1] - x + [2]**2/[0] ) ) * TMath::Erfc( 1./(sqrt(2)*[2]) * ( [1] - 2*[2]**2/[0] - x ) )' , -2, 6 )
	#fit2 = TF1("fit","myfit(0)+myfit(4)",2000,4000)
	fit.SetParameter( 1, mean)
	fit.SetParameter( 2, sigma )
	fit.SetParameter(0, 1500)
	#signal.Draw()
	#~ fit.Draw("same")
	signal.Fit('myfit')
	raw_input()


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

#FitTau(alutime,cotime,True)
#FitTau(calculateDeconvolution( alutime, cotime ))
