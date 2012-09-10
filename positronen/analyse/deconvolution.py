#!/usr/bin/python
# -*- coding: utf-8 -*-

from ROOT import TH1F,TSpectrum, TLegend, TCanvas
from numpy import array

from plotSpectrum import *
'''
can = TCanvas()
can.cd()
can.SetBatch()
'''
background= tkaToHist( 'data/co60.TKA', 1, 400 )
background.SetNormFactor(1.)
alu = tkaToHist( 'data/aluminium.TKA', 1, 400 )
alu.SetNormFactor(1.)
'''
background.SetLineColor(3)
background.Draw()
alu.Draw("same")
leg = TLegend(0.7, 0.7, 1,1)
leg.AddEntry( alu, "Aluminium")
leg.AddEntry( background, "Background")
leg.Draw()

can.SaveAs('firstComparison.pdf')
'''


def createTestHistos():
	sigma = 0.5
	tau = 1
	nbins = 100
	xmin  = -5
	xmax  = 5
	h = TH1F("h","Deconvolution",nbins,xmin,xmax)
	d = TH1F("d","",nbins,xmin,xmax)
	from ROOT import TRandom3
	r = TRandom3()
	for i in range( int(1e6) ):
		d.Fill( r.Gaus(0, sigma) )
		h.Fill( r.Gaus(0, sigma) + r.Exp(tau) )


	return h, d

def histToArray( histo ):
	from numpy import array
	nbins = histo.GetNbinsX()
	values = array( [0] * nbins, dtype = 'f' )
	for i in range( nbins ):
		values[i] = histo.GetBinContent(i + 1)

	return values

def deconvolution( signal, background ):
	source = histToArray( signal )
	response = histToArray( background )
	s = TSpectrum();
	s.Deconvolution(source, response, len( source ), 1000, 1, 1 )

	from ROOT import TH1D
	d = TH1D('', 'title', len(source), 1,400 )
	for i in range( len(source) ):
		d.SetBinContent(i + 1,source[i])
	d.Draw()
	raw_input()

def centroidShift( signal, background, xmin = 0, xmax  = 10000 ):
	signal.GetXaxis().SetRange( xmin, xmax ) # if integer -> bins, else user-range
	background.GetXaxis().SetRange( xmin, xmax ) # if integer -> bins, else user-range
	t = ( signal.GetMean() - background.GetMean() ) * signal.GetBinWidth(0)
	from math import sqrt
	s = sqrt ( signal.GetRMS()**2 / ( signal.GetEntries() -1 ) + background.GetRMS()**2 / (background.GetEntries() -1 ) )
	return t, s

print centroidShift( alu, background)




#deconvolution( alu, background )
