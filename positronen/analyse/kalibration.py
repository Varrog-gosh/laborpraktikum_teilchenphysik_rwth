#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()
from tools import *
import ROOT

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

	distance = 50 # minimal distance between channels

	# clear array of double peaks, which have less than distance channels distance
	for i in range( len(peaks) - 2, -1, -1):
		if peaks[i+1] - peaks[i] <  distance :
			del peaks[i+1]
			npeaks -= 1


	# fit gaus functions
	x = []
	ex = []
	for peak in peaks:
		fit = ROOT.TF1('fit', 'gaus', peak - distance/3, peak + distance/3)
		fit.SetParameters( hist.GetBinContent( hist.FindBin( peak ) ), peak, 5 )
		hist.Fit('fit', 'rq')
		if peak - fit.GetParameter(1) > 4:
			print 'Zu große abweichung von fit zu peakfinder bei ', peak
		else:
			x.append( fit.GetParameter(1) )
			ex.append( fit.GetParameter(2) ) # use σ for fit, and not error or mean, is this correct?

	valError = [x, ex]

	return valError

def kalibration( filename, firstpeak, minKanal = 0, maxKanal = 0 ):
	y, ey = peakToArray( filename, minKanal, maxKanal )
	x = []
	timestep = 0.5
	for i in range( len(y) ):
		x.append( timestep * (i + firstpeak) )
	ex = [0.1]*len(y)
	reg = linearRegression( x, y, ex, ey)
	reg.draw(';t [ns];Kanalnummer')
	reg.canvas.SaveAs('kalibration_regression.pdf')

	return reg.func



def tkaToTimeHist( filename , func, nBins, xMin, xMax ):
	'''
	not used now, and will never be used
	'''
	from ROOT import TH1F

	data = readFile( filename )[0]
	length = len( data )

	hist = TH1F('', ";Kanalnummer;Eintr#\"age", nBins, xMin, xMax )
	for i in range( nBins ):
		hist.SetBinContent( i, 1. / func.GetParameter(1) * (data[ i ] - func.GetParameter(0) ) )
		# what happens to the error of the regression?
	return hist


kalibration('data/kali_montag.TKA', 1, 1000 ) # number of first peak ( x%in = 2000 -> firstpeak = 1 )



