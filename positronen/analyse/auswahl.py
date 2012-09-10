#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()
import ROOT

def tkaToHist( filename , xMin = 0, xMax = 0 ):
	import tools
	from ROOT import TH1F

	data = tools.readFile( filename )[0]
	length = len( data )

	if xMax == 0:
		xMax = length
	length = int( xMax - xMin )

	hist = TH1F('', ";Kanalnummer;Eintr#ddot{a}ge", length, xMin-0.5, xMax-0.5 )
	for i in range( length ):
		hist.SetBinContent(i, data[ i + xMin ] )
	return hist


def plotSpectrum():
	hist = tkaToHist( 'data/co60.TKA', 0, 10500 )

	can = ROOT.TCanvas()
	can.cd()
	can.SetLogy()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	hist.Draw()

	grenzkanal = 4000
	line = ROOT.TLine( grenzkanal, hist.GetMinimum(), grenzkanal, hist.GetMaximum() )
	hist.Draw()
	line.Draw()

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



