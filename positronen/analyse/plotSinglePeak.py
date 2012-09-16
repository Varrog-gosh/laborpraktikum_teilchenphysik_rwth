#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()
from ROOT import TCanvas, TH1, TF1, TGraphErrors
from tools import *
from kalibration import *

def plotSinglePeak( filename = 'data/kali_montag.TKA' ):
	x, ex = peakToArray( filename, 100, 0)
	border = 55
	can = TCanvas('singlePeak')
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	for peak in [16]:
		print peak
		hist = tkaToHist( filename, int(x[peak]) - border, int(x[peak]) + border )
		hist.Draw()
		hist.SetNormFactor(1)
		can.Update()
		#raw_input()
	can.SaveAs('singlePeak.pdf')
	can.Close()

plotSinglePeak()

