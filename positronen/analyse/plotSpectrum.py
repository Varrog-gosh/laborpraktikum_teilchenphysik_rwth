#!/usr/bin/python
# coding = utf8
from Styles import tdrStyle
tdrStyle()
import ROOT

def tkaToHist( filename , xMin = 0, xMax = 0 ):
	import tools
	from ROOT import TH1F

	data = tools.readFile( filename )[0]
	length = len( data )

	if xMax == 0:
		xMax = length - 0.5
	else:
		xMax -= 0.5
	xMin -= 0.5
	length = int( xMax - xMin )

	hist = TH1F('', ";Kanalnummer;Eintr#ddot{a}ge", length, xMin, xMax )
	for i in range( int(xMin - 0.5), int(xMax-0.5) ):
		hist.SetBinContent(i, data[i] )
	return hist



def plotSpectrum():
	hist = tkaToHist( 'data/auswahl.TKA', 0, 10500 )

	can = ROOT.TCanvas()
	can.cd()
	can.SetLogy()
	can.SetBatch()
	can.SetCanvasSize( 1300, 500 )
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



def spectrum():
	#hist = tkaToHist( 'data/kali_ohne_threshold.TKA' )
	hist = tkaToHist( 'data/kali.TKA' , 4000)
	from ROOT import TCanvas, TSpectrum
	from numpy import array

	s = TSpectrum( 350 ) #max number of peaks
	npeaks = s.Search( hist, 2, "", 0.001 ) # ( hist, sigma, '', threshold )

	peaks = s.GetPositionX()
	peaksOrder = []
	for i in range( npeaks ):
		peaksOrder.append( peaks[i] )
	peaksOrder.sort()
	peakHeight = s.GetPositionY()
	deltapeaks = peaks[npeaks-1] - peaks[npeaks-2] # distance between peaks
	hist.Draw()
	raw_input()
	import ROOT

	import numpy
	graph = ROOT.TGraph()
	meas_points = range(21)
	meas_points.pop(4)
	meas_points.pop(13)
	meas_points.pop(11)
	meas_points.pop(20)
	graph.SetTitle(';t [ns]; Kanalnummer')
	for i in range( npeaks):
		#fit = ROOT.TF1('fit', 'gaus', peaks[i] - deltapeaks/2, peaks[i] + deltapeaks/2)
		#fit.SetParameters( peakHeight[i], peaks[i], deltapeaks/4 )
		#hist.Fit('fit', 'rq')
		graph.SetPoint( i, 0.5 * i, peaksOrder[i] )
		#print fit.GetParameter(1)
	hist.Draw()
	return graph

spectrum()



