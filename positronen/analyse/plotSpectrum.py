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
raw_input()

def peakToArray( filename, minKanal = 0, maxKanal = 0 ):
	hist = tkaToHist( filename , minKanal, maxKanal )
	from ROOT import TCanvas, TSpectrum, TGraph
	from numpy import array

	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.SetLogy()
	can.cd()


	s = TSpectrum( 64 ) #max number of peaks
	npeaks = s.Search( hist, 3, "", 0.005 ) # ( hist, sigma, '', threshold )
	hist.Draw()
	can.SaveAs('peaksToArray.pdf')

	peaks = s.GetPositionX()
	peakHeight = s.GetPositionY()

	deltapeaks = 250 # differenze between peaks

	x = []
	ex = []

	for i in range( npeaks ):
		fit = ROOT.TF1('fit', 'gaus', peaks[i] - deltapeaks/3, peaks[i] + deltapeaks/3)
		fit.SetParameters( peakHeight[i], peaks[i], 5 )
		hist.Fit('fit', 'rq')
		if peaks[i] - fit.GetParameter(1) > 1:
			print 'Zu große abweichung bei ', peaks[i]
		x.append( fit.GetParameter(1) )
		ex.append( fit.GetParameter(2) ) # use σ for fit, and not error or mean, is this correct?

	# sort arrays with errors
	valError = [x, ex]
	valError = map( list, zip( *valError ) ) # transpose
	valError.sort( key = lambda a: a[0] )
	valError = map( list, zip( *valError ) ) # transpose back

	return valError

def kalibration( filename, minKanal = 0, maxKanal = 0 ):
	y, ey = peakToArray( filename, minKanal, maxKanal )
	x = []
	for i in range( len(y) ):
		timestep = 0.5
		x.append( timestep * i )
	ex = [0]*len(y)
	import tools
	reload(tools)
	reg = tools.linearRegression( x, y, ex, ey)
	reg.draw(';t [ns];Kanalnummer')
	reg.canvas.SaveAs('kalibration_regression.pdf')

	return reg.func


def tkaToTimeHist( filename , func, nBins, xMin, xMax ):
	import tools
	from ROOT import TH1F

	data = tools.readFile( filename )[0]
	length = len( data )

	hist = TH1F('', ";Kanalnummer;Eintr#ddot{a}ge", nBins, xMin, xMax )
	for i in range( nBins ):
		hist.SetBinContent( i, 1. / func.GetParameter(1) * (data[ i ] - func.GetParameter(0) ) )
		# what happens to the error of the regression?
	return hist


kalibration('data/kali_montag.TKA', 500 )
#kalibration('data/kali_ohne_threshold.TKA', 3500, 12000 )






