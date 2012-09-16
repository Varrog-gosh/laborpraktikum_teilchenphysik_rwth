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
	hist = tkaToHist( filename , minKanal, maxKanal )
	from ROOT import TSpectrum
	from numpy import array
	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.SetLogy()
	can.cd()
	hist.Draw()
	s = TSpectrum( 64 ) #max number of peaks
	npeaks = s.Search( hist, 8, "", 0.005 ) # ( hist, sigma, '', threshold )
	#can.SaveAs('peaksToArray.pdf')
	can.Close()
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
	valError = [x, ex]
	can.Close()
	return valError

def kalibration (filename = 'data/kali_montag.TKA', firstpeak = 0, minKanal = 100, maxKanal = 0):
	x, ex = peakToArray( filename, minKanal, maxKanal )
	from array import array
	y = array('d')
	ey = array ('d')
	timestep = 0.5
	for i in range( len(x) ):
		y.append( timestep * (i + firstpeak) )
		ey.append(0.075)
	reg = linearRegression(x, y, ex, ey, 4000)
	reg.draw(';Kanal;t [ns]')
	reg.canvas.SaveAs('fit.pdf')
	reg.canvas.Close()
	return reg.func

def tkaToTimeHist( filename , func, timeshift = 0): #4720.6 ):
	import tools
	can = TCanvas()
	can.cd()
	hist = tkaToHist(filename )
	hist.SetTitle(';t [ns];Eintr#ddot{a}ge')
	a = hist.GetXaxis()
	xmin = func.Eval(0 - timeshift )
	xmax = func.Eval( a.GetNbins() - timeshift )
	a.Set( a.GetNbins(), xmin, xmax )
	hist.Draw()
	can.SaveAs('blub.pdf')
	return hist

func = kalibration()
c1 = TCanvas()
c1.cd()
hist = tkaToTimeHist( 'data/co60_2.TKA', func )
hist.Draw()
c1.SaveAs('timehist.pdf')

