#!/usr/bin/python
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()
from ROOT import TCanvas, TH1, TF1, TGraphErrors
from sys import exit
from tools import *

def bufferToSortedList( length, buffer ):
	output = []
	for i in range( length ):
		output.append( buffer[i] )
	return sorted( output )

def peakToArray( filename, minKanal , maxKanal ):
	'''
	get the sorted x position of peaks in kalibrationfile + errors
	returns: list[ x, ex ]
	'''
	hist = tkaToHist( filename , minKanal, maxKanal )
	from ROOT import TSpectrum
	from numpy import array
	can = TCanvas('peak_to_array')
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.SetLogy()
	can.cd()
	hist.Draw("hist")
	s = TSpectrum( 64 ) #max number of peaks
	npeaks = s.Search( hist, 8, "hist", 0.005 ) # ( hist, sigma, '', threshold )
	can.SaveAs('peaksToArray.pdf')
	peaks = bufferToSortedList( npeaks, s.GetPositionX() )
	distance = 50 # minimal distance between channels
	# clear array of double peaks, which have less than distance channels distance
	for i in range( len(peaks) - 2, -1, -1):
		if peaks[i+1] - peaks[i] <  distance :
			del peaks[i+1]
			npeaks -= 1
	from array import array
	# fit gaus functions
	x = array('d')
	ex = array('d')
	for peak in peaks:
		fit = TF1('fit', 'gaus', peak - distance/3, peak + distance/3)
		fit.SetParameters( hist.GetBinContent( hist.FindBin( peak ) ), peak, 5 )
		hist.Fit('fit', 'rq')
		if peak - fit.GetParameter(1) > 4:
			print 'Zu große abweichung von fit zu peakfinder bei ', peak
		else:
			x.append( fit.GetParameter(1) )
			ex.append( fit.GetParameter(2) ) # use σ for fit, and not error or mean, is this correct?
	can.Close()
	return [x, ex]


def kalibration (filename = 'data/kali_montag.TKA', beginning = 4200, firstpeak = 0, minKanal = 100, maxKanal = 0):
	'''
	calibrates spetrum with peaks
	filename: filename for calibration
	beginning: channel# when fit should start
	firspeak: first peak that is drawn
	minKanal: MUST be changed when firstpeak is variated.
				look at the histogram 'peakToArrays' to find suitiable values
	maxKanal: maximal channel, 0 means all

	returns: linear fit function TF1
	'''
	x, ex = peakToArray( filename, minKanal, maxKanal )
	from array import array
	y = array('d')
	ey = array ('d')
	timestep = 0.5
	for i in range( len(x) ):
		y.append( timestep * (i + firstpeak) )
		ey.append(0.075)
	reg = linearRegression(x, y, ex, ey, beginning)
	reg.draw(';Kanal;t [ns]')
	reg.canvas.SaveAs('linearRegression.pdf')
	reg.canvas.Close()
	return reg.func

def tkaToTimeHist( filename , func, xmin = -20, xmax = 20, channelShift = 4720.6 ):
	'''
	returns kalibrated hist from TKA file
	filename: filename of TKA file
	func: linear fit function for calibration channel vs. time
	xmin: minimal time of histogram, cant get larger than default range
	xmax: maximal time of histogram
	channelShift: #channels to shift cobalt peak to 0

	returns: histogram
	'''
	import tools
	hist = tkaToHist(filename)
	hist.SetTitle(';t [ns];Eintr#ddot{a}ge')
	a = hist.GetXaxis()
	xmin_orig = func.Eval(0 - channelShift ) - func.Eval(0)
	xmax_orig = func.Eval( a.GetNbins() - channelShift ) - func.Eval( 0 )
	a.Set( a.GetNbins(), xmin_orig, xmax_orig )

	if xmin < xmin_orig:
		xmin = xmin_orig
	if xmax > xmax_orig:
		xmax = xmax_orig

	# BinWidth is chosen that error of calibration negletiable
	from math import sqrt
	delta_t = sqrt( func.GetParError(0)**2 + func.GetParError(1)**2 * a.GetNbins()**2)
	hist.Rebin( int( delta_t / a.GetBinWidth(1) ) )
	a.SetRangeUser( xmin, xmax )

	return hist

# example how to call function
#func = kalibration( )
#hist = tkaToTimeHist( 'data/aluminium.TKA', func , -2, 8 )
