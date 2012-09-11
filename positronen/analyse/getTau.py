#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
from tools import *
from ROOT import *
from ROOT import TSpectrum
from Styles import tdrStyle
from array import array
tdrStyle()

cobalt = tkaToHist( 'data/co60.TKA', 1, 400 )
cobalt.SetNormFactor(1.)
alu = tkaToHist( 'data/aluminium.TKA', 1, 400 )
alu.SetNormFactor(1.)

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

def deconvolution( signal, background ):
	'''
	using roots deconvolution class
	τ in chanel numbers is printed
	'''
	from ROOT import TH1D,TSpectrum, TF1
	source = histToArray( signal )
	response = histToArray( background )
	s = TSpectrum();
	s.Deconvolution(source, response, len( source ), 1000, 1, 1 )

	d = TH1D('', 'Kanalnummer;Eintr#ddot{a}ege', len(source), 1,400 )
	for i in range( len(source) ):
		d.SetBinContent(i + 1,source[i])
	d.Draw()
	fit = TF1('fit', 'expo',40, 200)
	d.Fit('fit', 'r')
	print -1. / fit.GetParameter(1)
	raw_input()

def centroidShift( signal, background, xmin = 0, xmax  = 10000 ):
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

def getBackground ():
	
	
	spec = tkaToHist('data/co60.TKA',20,350)
	nbins = array('i')
	nbins.append( spec.GetNbinsX() )
	xmin  = 20;
	xmax  = 200;
	print "nbins[0] %i"%nbins[0]
	source = numpy.zeros(nbins[0],dtype=float)
	d = spec.Clone()
	#~ d =  TH1F("d","",nbins[0],xmin,xmax);
   #TFile *f = new TFile("spectra\\TSpectrum.root");
	#~ spec.Draw("L")
	
   #back->Draw("L");
	s =TSpectrum();
	for i in range(0,nbins[0]):
		source[i] = spec.GetBinContent(i + 1)
		print "%i %d"%(i,source[i])
	#~ s.Background(source,nbins[0],6,'kBackDecreasingWindow','kBackOrder2','kFALSE','kBackSmoothing3','kFALSE')
	#~ for i in range(nbins[0]):
		#~ d.SetBinContent(i + 1,source[i])
	d = s.Background(spec,5)
	d.SetLineColor(kRed)
	#~ d.Draw("sameL")
	sig = substractHist(spec,d)
	plotDataAndBackground(spec,sig)
	
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
	can.SetLogy()
	background.SetLineColor(3)
	background.Draw()
	#~ alu.Draw("same")
	signal.Draw("same")
	leg = TLegend(0.7, 0.7, 1,1)
	leg.AddEntry( alu, "Aluminium", "l")
	leg.AddEntry( background, "Background", "l")
	leg.Draw()

	can.SaveAs('firstComparison.pdf')


# execute programs
#~ print centroidShift( alu, cobalt)
#~ deconvolution( alu, cobalt )
#~ plotDataAndBackground( alu, cobalt )
getBackground()
#~ safeHist(cobalt)

