#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *
from tools import *

def getMass( dataTree, mcTree, cut, save, variable,quiet=0 ):
	nBins = 20
	if variable=="mwt":
		firstBin = 60
		lastBin =180
		affix = ""
		xmin = 79.4
		xmax = 81.
	else:
		firstBin = 30
		lastBin = 100
		xmin= 79.8
		xmax =81.
		affix = "et"
	#~ nBins2 = 4./(lastBin -firstBin)*nBins
	#~ drawhist = createHistoFromTree(dataTree, variable, cut, nBins2, 78 , 82)
	datahist = createHistoFromTree(dataTree, variable, cut, nBins, firstBin, lastBin)
	datahist.Scale( 1./datahist.Integral() )
	from ROOT import TGraph, TCanvas
	from array import array
	can = TCanvas( randomName(), "template", 1400, 800 )
	can.cd()
	if save or quiet:
		can.SetBatch()

	x = array('d')
	y = array('d')
	masses = weightToMass()
	for i, mass in enumerate( masses ):
		x.append( mass )
		mchist = createHistoFromTree( mcTree, variable, 'weight['+str(i)+'] * ('+cut+')', nBins, firstBin, lastBin)
		mchist.Scale( 1./mchist.Integral() )
		datahist.SetTitle( ';'+cut)
		chi2ndf = datahist.Chi2Test( mchist, "WW,chi2/ndf")
		y.append( chi2ndf )
	gr = TGraph(len(masses), x,y)
	gr.SetTitle(';M_{W} [GeV];#chi^{2}/NDF')
	
	gr.Fit('pol2','q0',"X",78,82)
	gr.GetFunction('pol2').SetParNames("a", "b", "c")
	gr.GetFunction('pol2').SetRange(xmin,xmax)
	gr.GetFunction('pol2').Draw("RL")
	gr.Draw("psame")
	# draw cut as text
	from ROOT import TPaveText
	text = TPaveText(0.2, 0.85, .8, .95, 'ndc')
	text.SetFillStyle(0)
	text.SetBorderSize(0)
	from re import sub
	niceVariable = sub('el_et', 'E_{T}', variable )
	niceVariable = sub('mwt', 'm_{T}', variable )
	text.AddText( "Benutzte Variable: " + niceVariable )
	text.AddText( prettifySelection( cut ) )
	text.Draw()


	if save:
		can.SaveAs('template'+affix+'.pdf')
	elif quiet==False:
		can.Update()
		raw_input()
	func = gr.GetFunction('pol2')
	mass = -func.GetParameter(1) / (2 * func.GetParameter(2))

	chi2min = func.Eval( mass )
	offset = 1 # how much χ² should change for error
	from math import sqrt
	try:
		e_mass = sqrt( 1.* offset / func.GetParameter(2) )
	except:
		e_mass = 0

	return mass, e_mass, 0.78 #wert, err_mass (stat.), err_mass (sys.)


def getXs(dataTree,mcTree,variable,cut):
	#returns crosssection
	#uses efficiency e eff = n_after_cut / n_generated
	from math import sqrt
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	nBins = 10 # default value
	ngen = 1164699.
	mcHisto = createHistoFromTree( mcTree, variable, cut, nBins, xlow, xhigh )
	n_after_cut = 1.*mcHisto.GetEntries()
	eff = n_after_cut / ngen
	print "Efficiency: %.3f" %eff
	dataHisto = createHistoFromTree( dataTree, variable, cut, nBins, xlow, xhigh )
	n_obs = dataHisto.GetEntries()
	lumi = 198e3
	err_lumi = 20e3
	corr = 0.9
	err_corr = 0.1
	xs = n_obs / eff / lumi / corr
	err_xs_stat = xs / sqrt(n_obs)
	err_xs_sys = xs * sqrt(1/ngen + 1/n_after_cut + pow(err_corr/corr,2) + pow(err_lumi/lumi,2))
	return xs,err_xs_stat,err_xs_sys

def Compare_val(val,err_val_stat,err_val_sys,val_theo,err_theo):
	#function returns how many standard deviations are between theory
	# and measurement
	from math import sqrt
	d = 1. * abs(val_theo - val)
	err_comb = sqrt(err_val_stat**2 + err_val_sys **2 + err_theo**2 )
	return d/err_comb

def getWeinberg (mw,err_mw_stat,err_mw_sys):
	mz = 91.227
	err_mz = 0.041
	sin2_wein = 1- pow(mw / mz,2)
	from math import sqrt
	err_sin2_wein_sys = sqrt(pow(2 * mw * err_mw_sys / mz**2 ,2) + pow( 2* mw**2 * err_mz / mz**3 ,2))
	err_sin2_wein_stat = 2. * mw * err_mw_stat / mz**2
	return sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys

def getWidth (mw, err_mw_stat, err_mw_sys ):
	from math import sqrt

	# known variables
	alpha = 1.0/128
	mz = 91.227
	err_mz_sys = 0.041

	mr2 = ( mw/mz )**2 # mass ratios squared, often used variable
	# do not use sin²θ here to avoid correlations
	gamma = 3./4 * alpha * mw / (1 - mr2 )
	err_gamma_stat = 3./4*alpha * (1 + mr2 ) / ( 1 - mr2)**2 * err_mw_stat
	err_gamma_sys = 3./4*alpha * sqrt ( ( (1+mr2)/(1-mr2)**2 * err_mw_sys )**2 + ( 2*mr2*mw/mz/(1-mr2)**2 * err_mz_sys )**2 )
	return gamma,err_gamma_stat,err_gamma_sys

def getxsNC (xs,err_xs_stat,err_xs_sys):
	from math import sqrt
	xs3,exs3 = 2.58,0.09
	eci = 0.09

	ci = 2./3
	xs2 = ci * xs3
	exs2 = sqrt(xs3**2 * ci**2 * eci**2 + ci**2 * exs3**2)
	eci = 0.04
	ci = 4./3
	xs4 = ci * xs3
	exs4 = sqrt(xs3**2 * ci**2 * eci**2 + ci**2 * exs3**2)
	return [[2,3,4],[xs2,xs3,xs4],[exs2,exs3,exs4]]

def CompareNC (xs,err_xs_stat,err_xs_sys):
	theo = getxsNC(xs,err_xs_stat,err_xs_sys)
	print "measured: σ = %.2f \pm %.2f/ (stat.) \pm %.2f (sys.) nb"%(xs,err_xs_stat,err_xs_sys)
	for i in range(len(theo[0])):
		print "theory: \n Nc = %d σ = %.2f \pm %.2f/ nb"%(theo[0][i],theo[1][i],theo[2][i])
		print "%.2f standard deviations between theory and measurement"%Compare_val(xs,err_xs_stat,err_xs_sys, theo[1][i], theo[2][i])

if (__name__ == "__main__"):
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("-m", "--mcfile", dest="mcfile", default="mc_all_new.root/MCTree", help="MC file path")
	parser.add_argument("-d", "--datafile", dest="datafile", default="d0_new.root/MessTree", help="Data file path")
	parser.add_argument("-c", "--cut", dest="cut", default="met > 30 && el_et > 30", help="Cuts applied to all structures" )
	parser.add_argument("--save", action="store_true", default=False, help="Plots are not drawn, but saved as pdf")
	parser.add_argument("-p", "--plots", dest="plots", default= "mwt")
	parser.add_argument("-q", "--quiet", dest="quiet", default= "0")

	opts = parser.parse_args()
	import Styles # official cms style
	style = Styles.tdrStyle()
	mcTree = readTree( opts.mcfile )
	dataTree = readTree( opts.datafile )

	m, e_m,e_m_sys = getMass( dataTree, mcTree, opts.cut, opts.save, opts.plots ,int(opts.quiet))
	sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys = getWeinberg( m, e_m ,e_m_sys)
	gamma,err_gamma_stat,err_gamma_sys = getWidth(m, e_m, e_m_sys )
	
	print "Mass: %.2f \pm %.2f/ (stat.) \pm %.2f (sys.) GeV"%(m, e_m,e_m_sys)
	print
	if (int(opts.quiet) == 0):
		xs,err_xs_stat,err_xs_sys = getXs(dataTree,mcTree,opts.plots,opts.cut)
		print "Crosssection: σ = %.2f \pm %.2f/ (stat.) \pm %.2f (sys.) nb"%(xs,err_xs_stat,err_xs_sys)
		print "Theory Crossection: σ = %.2f \pm %.2f nb"%(2.58,0.09)
		print "The Crossection deviates %f standard deviations from the theoretical value "%Compare_val(xs,err_xs_stat,err_xs_sys,2.58,0.09)

		print
		print 'Weinbergangle: sin²θ = %.4f \pm %.4f (stat.) \pm %.4f (sys.)'%(sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys)
		print 'Weinbergangle (corrected): sin²θ = %.4f \pm %.4f (stat.) \pm %.4f (sys.)'%(sin2_wein*1.06,err_sin2_wein_stat*1.06,err_sin2_wein_sys*1.06)
		print "Weinbergangle theory: sin²θ = %.4f \pm %.4f "%(0.2397, 0.0013)
		print "Angle(uncorrected) deviates %f standard deviations from the theoretical value "%Compare_val(sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys, 0.2397, 0.0013)
		print "Angle(corrected) deviates %f standard deviations from the theoretical value "%Compare_val(sin2_wein*1.06,err_sin2_wein_stat*1.06,err_sin2_wein_sys*1.06, 0.2397, 0.0013)
		print ""
		print 'W-Width: Γ = %.4f \pm %.4f (stat.) \pm %.4f (sys.)'%(gamma,err_gamma_stat,err_gamma_sys)
		print "Width deviates %f standard deviations from the theoretical value "%Compare_val(gamma,err_gamma_stat,err_gamma_sys, 2.141, 0.041)
		CompareNC(xs,err_xs_stat,err_xs_sys)
