#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *
from tools import *

def getMass( dataTree, mcTree, cut, variable = 'mwt' ):
	nBins = 20
	firstBin = 80
	lastBin = 90
	datahist = createHistoFromTree(dataTree, variable, cut, nBins, firstBin, lastBin)
	datahist.Scale( 1./datahist.Integral() )

	from ROOT import TGraph
	from array import array
	x = array('d')
	y = array('d')
	masses = weightToMass()
	for i, mass in enumerate( masses ):
		x.append( mass )
		mchist = createHistoFromTree( mcTree, variable, 'weight['+str(i)+'] * ('+cut+')', nBins, firstBin, lastBin)
		mchist.Scale( 1./mchist.Integral() )
		datahist.SetTitle( ';'+cut)
		chi2ndf = datahist.Chi2Test( mchist, "WW,of,uf,chi2/ndf")
		y.append( chi2ndf )
	gr = TGraph(len(masses), x,y)
	gr.SetTitle(';M_{W} [GeV];#chi^{2}/NDF')
	gr.Draw("ap")
	gr.Fit('pol2','q')
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

	return mass, e_mass,0.0 #wert, err_mass (stat.), err_mass (sys.)


def Get_xs(dataTree,mcTree,variable,cut):
	#returns crosssection
	#uses efficiency e eff = n_after_cut / n_generated
	from math import sqrt
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	nBins = 10 # default value
	ngen = 1164699
	mcHisto = createHistoFromTree( mcTree, variable, cut, nBins, xlow, xhigh )
	n_after_cut = mcHisto.GetEntries()
	eff = n_after_cut / ngen
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
	err_comb = sqrt(err_val_stat**2 + err_val_sys **2 )
	d = abs(val_theo - val)
	d_err = sqrt(err_comb+err_theo)
	return d/d_err

def getWeinberg (mw,err_mw_stat,err_mw_sys):
	mz = 91.227
	err_mz = 0.041
	sin2_wein = 1- pow(mw / mz,2)
	from math import sqrt
	err_sin2_wein_sys = sqrt(pow(2 * mw * err_mw_sys / mz**2 ,2) + pow( 2* mw**2 * err_mz / mz**3 ,2))
	err_sin2_wein_stat = 2. * mw * err_mw_stat / mz**2
	return sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys
	
def getWwidth (mw,err_mw_stat,err_mw_sys,sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys):
	from math import sqrt
	alpha = 1.0/127
	gamma = 3./4 * alpha * mw / sin2_wein
	err_gamma_stat = 3./4*alpha * sqrt(pow(err_mw_stat / sin2_wein,2) + pow(mw * err_sin2_wein_stat / sin2_wein**2,2))
	err_gamma_sys = 3./4*alpha * sqrt(pow(err_mw_sys / sin2_wein,2) + pow(mw * err_sin2_wein_sys / sin2_wein**2,2))
	return gamma,err_gamma_stat,err_gamma_sys

def printTheoreticalValues():
	print '                     THEORY'
	print 'Mass = ',
	printError( 80.385, 0.015, 'GeV')
	print 'sin²θ = ',
	printError( 0.2397, 0.0013 )
	print '               ( sollte 6% größer als unserer)'
	print 'σ = ',
	printError( 2.58,0.09, 'nb')
	print 'Γ = ',
	printError( 2.085, 0.042, 'nb')

if (__name__ == "__main__"):
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("-m", "--mcfile", dest="mcfile", default="mc_all_new.root/MCTree", help="MC file path")
	parser.add_argument("-d", "--datafile", dest="datafile", default="d0_new.root/MessTree", help="Data file path")
	parser.add_argument("-c", "--cut", dest="cut", default="1", help="Cuts applied to all structures" )
	parser.add_argument("-l", "--logarithmic", dest="logarithmic", default=True, help="Plot all distributions in logarithmic mode") #not implemented yet
	parser.add_argument("-s", "--save", dest="save", default=False, help="Plots are not drawn, but saved as pdf") #not implemented yet
	parser.add_argument("-p", "--plots", dest="plots", default=['met', 'el_et','mwt'], nargs ="+",
			help="Distribution which should be plotted")

	opts = parser.parse_args()
	import Styles # official cms style
	style = Styles.tdrStyle()
	mcTree = readTree( opts.mcfile )
	dataTree = readTree( opts.datafile )
	if "all" in opts.plots:
		opts.plots = histo_settings().keys()

	cut = 'met>30&& el_et > 30'# && mwt/el_et > 1.8'
	m, e_m,e_m_sys = getMass( dataTree, mcTree, cut, variable = 'mwt' )
	sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys = getWeinberg( m, e_m ,e_m_sys)
	gamma,err_gamma_stat,err_gamma_sys = getWwidth(m, e_m, e_m_sys, sin2_wein*1.06, err_sin2_wein_stat*1.06 ,err_sin2_wein_sys*1.06)
	print 'Mass =  ', printError(m, e_m, unit = 'GeV')
	xs,err_xs_stat,err_xs_sys = Get_xs(dataTree,mcTree,opts.plots[0],opts.cut)
	print "Crosssection: σ = %.2f \pm %.2f/ (stat.) \pm %.2f (sys.) nb"%(xs,err_xs_stat,err_xs_sys)
	print "Theory Crossection: σ = %.2f \pm %.2f nb"%(2.58,0.09)
	print "The Crossection deviates %f standard deviations from the theoretical value "%Compare_val(xs,err_xs_stat,err_xs_sys,2.58,0.09)
	print 'Weinbergangle: sin²θ = %.4f \pm %.4f (stat.) \pm %.4f (sys.)'%(sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys)
	print 'Weinbergangle (corrected): sin²θ = %.4f \pm %.4f (stat.) \pm %.4f (sys.)'%(sin2_wein*1.06,err_sin2_wein_stat*1.06,err_sin2_wein_sys*1.06)
	print "Weinbergangle theory: sin²θ = %.4f \pm %.4f "%(0.2397, 0.0013)
	print "Angle(uncorrected) deviates %f standard deviations from the theoretical value "%Compare_val(sin2_wein,err_sin2_wein_stat,err_sin2_wein_sys, 0.2397, 0.0013)
	print "Angle(corrected) deviates %f standard deviations from the theoretical value "%Compare_val(sin2_wein*1.06,err_sin2_wein_stat*1.06,err_sin2_wein_sys*1.06, 0.2397, 0.0013)
	print ""
	print 'W-Width: Γ = %.4f \pm %.4f (stat.) \pm %.4f (sys.)'%(gamma,err_gamma_stat,err_gamma_sys)
	print "Width deviates %f standard deviations from the theoretical value "%Compare_val(gamma,err_gamma_stat,err_gamma_sys, 2.085, 0.042)
