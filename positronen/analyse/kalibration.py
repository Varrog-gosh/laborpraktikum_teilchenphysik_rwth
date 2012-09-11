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

	from array import array
	# fit gaus functions
	x = array('d')
	ex = array('d')
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
	import tools
	reload(tools)
	reg = tools.linearRegression( x, y, ex, ey)
	reg.draw(';t [ns];Kanalnummer')
	reg.canvas.SaveAs('kalibration_regression.pdf')

	return reg.func

def kalibration_nonlin (filename, firstpeak, minKanal = 0, maxKanal = 0):
	y, ey = peakToArray( filename, minKanal, maxKanal )
	from array import array
	from ROOT import TF1
	from ROOT import TGraphErrors
	from ROOT import TCanvas
	
	can = TCanvas()
	can.SetBatch()
	can.SetCanvasSize( 1400, 800 )
	can.cd()
	
	x = array('d')
	ex = array ('d')
	timestep = 0.5
	for i in range( len(y) ):
		x.append( timestep * (i + firstpeak) )
		ex.append(0.1)
	#~ graph = TGraphErrors(len(y),x,y,ex,ey)
	graph = TGraphErrors(len(y),y,x,ey,ex)
	graph.Draw("AP")
	#~ graph.Print()
	#~ f1 = TF1("f1","[0]*sqrt((x-[1])**2-[2])",0.2,12.5);
	f1 = TF1("f1","[0]+[1]*x**2",1900,6103);
	#~ f1 = TF1("f1","[0]*sqrt(x**2-[1])",1900,16000);
	#~ f1.SetParameters(6.5e-8,0,0.25/6.5e-8)
	graph.Fit(f1,"R")
	f2 = TF1("f2","[0]+x*[1]",6000,16000);
	graph.Fit(f2,"R+")
	dif = f1.Eval(6000)-f2.Eval(6000)
	print "difference : %f"%dif
	
	
	#~ 
	#~ par0 = f1.GetParameter(0)
	#~ par1 = f1.GetParameter(1)
	#~ par2 = f2.GetParameter(0)
	#~ par3 = f2.GetParameter(1)
	#~ f_all = TF1("f2","[0]+x*[1]+[2]+x*[3]",1900,16000);
	#~ f_all.SetLineColor(3)
	#~ f_all.SetParameters(par0,par1,par2,par3)
	#~ graph.Fit(f_all,"R+")
	
	can.SaveAs('kalibration_nonlin.pdf')
	resi = y
	#~ for i in range(len(resi)):
		#~ if x[i] > 
		#~ resi[i] = y[i] - 	
	#~ raw_input()
	return [f1,f2]

def residuals(self):
		'''
		usually called by draw()
		calculates residuals
		'''
		from uncertainties import unumpy
		from numpy import array
		from ROOT import TGraphErrors
		residuals = self.__y
		for i in range( len( self.__x ) ):
			residuals[i] = self.__y[i] - self.func.Eval( self.__x[i] )
		self.resgraph = TGraphErrors( len( self.__x ), self.__x, residuals, self.__ex, self.__ey )

	
def tkaToTimeHist( filename , funcs, xmin_time,xmax_time,rebin ): #nBins, xMin, xMax,
	'''
	not used now, and will never be used
	'''
	import tools
	from ROOT import TH1F
	
	#~ data = tools.readFile( filename )[0]
	#~ length = len( data )
	#~ hist = TH1F('', ";Kanalnummer;Eintr#\"age", nBins, xMin, xMax )	
	hist = tkaToHist(filename)
	nBins = hist.GetNbinsX()
	hist_time = TH1F('', ";Zeit[ns];Eintr#\"age", nBins, xmin_time, xmax_time )
	histlist =[]
	print "xmin: %f xmax: %f "%(funcs[0].GetXmin() , funcs[0].GetXmax() )
	print "xmin: %f xmax: %f "%(funcs[1].GetXmin() , funcs[1].GetXmax() )
	for func in funcs:
		for i in range (nBins):
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
		if entry[1] < 0.01:
			print "bin %i val: %d"%( entry[0] ,entry[1] )
	hist_time.Rebin(rebin)
	return hist_time

def PlotHist(hist,title,xtitle,logmode = "0"):
	from ROOT import TCanvas
	
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
	can.SaveAs('hist_%s.pdf'%title)

fu = kalibration_nonlin('data/kali_montag.TKA', 1, 1000 ) # number of first peak ( x%in = 2000 -> firstpeak = 1 )
time_hist = tkaToTimeHist( "data/aluminium.TKA" , fu,0,12,10)
hist = tkaToHist("data/aluminium.TKA",2000,16000)
PlotHist(hist,"Alu_channnel","channel")
PlotHist(time_hist,"Alu_time","t[ns]",1)
