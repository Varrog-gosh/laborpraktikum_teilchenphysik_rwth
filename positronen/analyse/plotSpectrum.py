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

def bufferToSortedList( length, buffer ):
	output = []
	for i in range( length ):
		output.append( buffer[i] )
	return sorted( output )


def peakToArray( filename, minKanal = 0, maxKanal = 0 ):
	hist = tkaToHist( filename , minKanal, maxKanal )
	from ROOT import TCanvas, TSpectrum, TGraph
	from numpy import array

	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.SetLogy()
	can.cd()
	hist.Draw()
	s = TSpectrum( 64 ) #max number of peaks
	npeaks = s.Search( hist, 8, "", 0.005 ) # ( hist, sigma, '', threshold )
	can.SaveAs('peaksToArray.pdf')

	peaks = bufferToSortedList( npeaks, s.GetPositionX() )
	for i in range( len(peaks) - 2, -1, -1): # clear array of double peaks
		if peaks[i+1] - peaks[i] < 50:
			del peaks[i+1]
			npeaks -= 1

	deltapeaks = 250 # differenze between peaks

	x = []
	ex = []
	for peak in peaks:
		fit = ROOT.TF1('fit', 'gaus', peak - deltapeaks/3, peak + deltapeaks/3)
		fit.SetParameters( hist.GetBinContent( hist.FindBin( peak ) ), peak, 5 )
		hist.Fit('fit', 'rq')
		if peak - fit.GetParameter(1) > 4:
			print 'Zu große abweichung bei ', peak
		else:
			x.append( fit.GetParameter(1) )
			ex.append( fit.GetParameter(2) ) # use σ for fit, and not error or mean, is this correct?

	# sort arrays with errors
	valError = [x, ex]
	valError = map( list, zip( *valError ) ) # transpose
	valError.sort( key = lambda a: a[0] )
	valError = map( list, zip( *valError ) ) # transpose back

	return valError

def kalibration( filename, firstpeak, minKanal = 0, maxKanal = 0 ):
	y, ey = peakToArray( filename, minKanal, maxKanal )
	x = []
	timestep = 0.5
	for i in range( len(y) ):
		x.append( timestep * (i + firstpeak) )
	ex = [0.1]*len(y)
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

	hist = TH1F('', ";Kanalnummer;Eintr#\"age", nBins, xMin, xMax )
	for i in range( nBins ):
		hist.SetBinContent( i, 1. / func.GetParameter(1) * (data[ i ] - func.GetParameter(0) ) )
		# what happens to the error of the regression?
	return hist


#kalibration('data/kali_montag.TKA', 1, 1000 ) # number of first peak ( x%in = 2000 -> firstpeak = 1 )



