#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
style = tdrStyle()
from tools import *
import ROOT

def plotSpectrum():
	'''
	plots the spectrum for data selection in the slow circuit
	'''
	hist = tkaToHist( 'data/auswahl.TKA', 0, 10500 )

	can = ROOT.TCanvas()
	can.cd()
	can.SetLogy()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	hist.SetMinimum(9)
	hist.Draw()

	grenzkanaele = [ 260, 3630] # richtige kanalnummer rausfinden
	lines = []
	hist.Draw()
	for grenzkanal in grenzkanaele:
		line = ROOT.TLine( grenzkanal, hist.GetMinimum(), grenzkanal, hist.GetMaximum() + 7500 )
		line.SetLineStyle(2)
		line.SetLineWidth(2)
		line.Draw()
		lines.append(line)

	# to adjust text to line
	textwidth = 3000
	textheight = 5000
	textlevel = 1000
	textdistance = 300

	t1  = ROOT.TPaveText( grenzkanal - textdistance - textwidth , textlevel, grenzkanal - textdistance, textlevel + textheight )
	t1.AddText('Fenster 1')
	t1.SetBorderSize(0)
	t1.SetFillColor(0)
	t1.Draw()

	t2  = ROOT.TPaveText( grenzkanal + textdistance , textlevel, grenzkanal + textdistance + textwidth, textlevel + textheight )
	t2.AddText('Fenster 2')
	t2.SetBorderSize(0)
	t2.SetFillColor(0)
	t2.Draw()
	can.SaveAs('auswahl.pdf')

plotSpectrum()


