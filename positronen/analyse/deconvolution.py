#!/usr/bin/python
# -*- coding: utf-8 -*-

from ROOT import TH1F,TSpectrum
from numpy import array

from plotSpectrum import *

hist = tkaToHist( 'data/co60.TKA' )
hist.Draw()



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
'''
u,v = createTestHistos()
source = histToArray( u )
response = histToArray( v )

s = TSpectrum();

s.Deconvolution(source, response, len( source ), 1000, 1, 1 )

from ROOT import TH1D
d = TH1D('', 'title', len(source), -5, 5 )
for i in range( len(source) ):
	d.SetBinContent(i + 1,source[i])
d.Draw()

'''
