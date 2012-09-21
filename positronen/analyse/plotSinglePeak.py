#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()
from ROOT import TCanvas, TH1, TF1, TGraphErrors, gStyle
from tools import *
from kalibration import *

def plotSinglePeak( filename = 'data/kali_montag.TKA' ):
	x, ex = peakToArray( filename, 100, 0)
	drawBorder = 40
	border = 22
	can = TCanvas('singlePeak')
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )

	gStyle.SetStatFontSize(0.07)

	for peak in [16]:
		print peak
		hist = tkaToHist( filename, int(x[peak]) - drawBorder, int(x[peak]) + drawBorder )
		hist.Sumw2()
		hist.Scale(1./hist.Integral())
		func = TF1('fit',"gaus", int(x[peak]) - border, int(x[peak]) + border)
		hist.Fit('fit', "r")
		hist.GetFunction('fit').SetParNames('N_{max}',"#mu", "#sigma")
		hist.Draw()
		can.Update()
		#raw_input()
	can.SaveAs('singlePeak.pdf')
	can.Close()

plotSinglePeak()

