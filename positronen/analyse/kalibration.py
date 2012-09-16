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
	# asume two linear functions
	# otherwise a numerical solver is of use to find the interception point
	cut = ( funcs[0].GetParameter(0) - funcs[1].GetParameter(0) ) / ( funcs[1].GetParameter(1) - funcs[0].GetParameter(1) )
	#cutbin = hist.FindBin( cut )
	hist1 = tkaToHist(filename, 0, int(cut) )
	hist2 = tkaToHist( filename, int(cut)+1, 0)
	hist1.Draw()
	hist2.Draw("same")
	raw_input()
	can.Close()
	exit()
	nBins = hist.GetNbinsX()
	hist_time = TH1('', ";Zeit[ns];Eintr#\"age", nBins, xmin_time, xmax_time )
	histlist =[]


	for i in range( cutbin ):
		a = hist.GetXaxis()
		import pdb; pdb.set_trace()

		hist_time.SetBinContent(i,3)
		if hist.GetBinLowEdge(i) > func.GetXmin() and hist.GetBinLowEdge(i)+ hist.GetBinWidth(i) < func.GetXmax():
				time_bin = hist_time.FindBin(  func.Eval( hist.GetBinCenter(i))  )
				histlist.append([time_bin,hist.GetBinContent(i)])
	
	sumval = 0
	final_histlist =[]
	#~ print histlist
	for i in range(len(histlist)):
		if i < len(histlist)-1:
			tbin1 = histlist[i][0]
			val1	 = histlist[i][1]
			tbin2 = histlist[i+1][0]
			val2	 = histlist[i+1][1]
			
			if abs(tbin1 - tbin2) < 0.0001:
				sumval+=val1
			else:
				if sumval > 0.0:
					final_histlist.append([tbin1,sumval])
				else:
					final_histlist.append([tbin1,val1])
				sumval = 0
	
	for entry in final_histlist:
		hist_time.SetBinContent(  entry[0] ,entry[1] )
	if rebin > 0.01:
		hist_time.Rebin(rebin)
	return hist_time


def PlotHist(hist,title,xtitle,logmode = "0"):
	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.cd()
	if logmode == 1:
		can.SetLogy()
	hist.SetTitle(title)
	hist.GetXaxis().SetTitle(xtitle)
	hist.GetYaxis().SetTitle("Eintr#ddot{a}ge")
	hist.Draw()
	can.SaveAs('blub.pdf')
	return hist

func = kalibration()
c1 = TCanvas()
c1.cd()
hist = tkaToTimeHist( 'data/co60_2.TKA', func )
hist.Draw()
c1.SaveAs('timehist.pdf')

