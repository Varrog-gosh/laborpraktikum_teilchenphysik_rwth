#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
from tools import *
from ROOT import *
from ROOT import TSpectrum
from Styles import tdrStyle
from array import array
tdrStyle()


def normedHist( name, color ):
	hist = tkaToHist( name, 2000, 16000 )
	hist.SetNormFactor(1.)
	hist.SetLineColor( color )
	return hist

alu = normedHist( 'data/aluminium.TKA' , 2)
poly = normedHist( 'data/poly.TKA' , 4)
co = normedHist( 'data/co60.TKA', 1 )

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
	from ROOT import TH1D,TSpectrum, TF1
	source = histToArray( signal )
	response = histToArray( background )
	s = TSpectrum();
	# parameters for deconvolution:
	# iterations = 1: more iterations -> stange peaks and more noice
	# rebetitions =  1: same as above
	# boosting factor = 1: not needed
	s.Deconvolution(source, response, len( source ), 1, 1, 1 )

	d = TH1D('', 'Kanalnummer;Eintr#ddot{a}ege', len(source), 1,16000 )
	for i in range( len(source) ):
		d.SetBinContent(i + 1,source[i])
	#safeHist( d, 'deconvolution100.root' )
	d.Draw()
	fitRanges = [ (3100, 6000) , (8000, 11000)]
	for fitRange in fitRanges:
		fit = TF1('fit', 'expo',fitRange[0], fitRange[1] )
		d.Fit('fit', 'r')
		print -1. / fit.GetParameter(1)
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
	can = TCanvas()
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
	can.SaveAs('compareHistos.pdf')

def tail( signal, background ):
	from ROOT import TH1
	# does not work yet
	onehisto = signal.DrawCopy(  )
	signal.Copy( onehisto )
	for i in range( onehisto.GetNbinsX() ):
		onehisto.SetBinContent( i+1, 1 )
	signal.Divide(background)
	onehisto.Add( signal, -1 )
	onehisto.Draw()
	raw_input()
#tail( alu, co )

# execute programs
calculateDeconvolution( alu, co )
#plotDataAndBackground( alu, co )
#print centroidShift( alu, co, 2000, 16000)
#compareSignalHistos( alu, poly )
