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

	return mass, e_mass


def Get_xs(dataTree,mcTree,variable,cut):
	#returns crosssection
	#uses efficiency e eff = n_after_cut / n_generated
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
	lumi = 198
	corr = 0.9
	xs = n_obs / eff / lumi / corr
	return xs

def getWeinberg (mw,err_mw):
	mz = 91.227
	err_mz = 0.041
	cos_wein = mw / mz
	from math import sqrt
	err_cos_wein = sqrt(err_mw**2 / mz**2 + mw**2 / mz**4 * err_mz**2)
	print "Cos(Theta) = %f +/- %f" % (cos_wein,err_cos_wein)
	return cos_wein,err_cos_wein

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
	m, e_m = getMass( dataTree, mcTree, cut, variable = 'mwt' )
	print 'Mass =  ',
	printError(m, e_m, unit = 'GeV')
	sigma, e_sigma = Get_xs(dataTree,mcTree,opts.plots[0], cut)
	print "σ = ",
	printError(sigma, esigma, unit = 'nb')
	sin2theta, e_sin2theta = getWeinberg( m, e_m )
	print 'sin²(θ) = ',
	printError( sin2theta, e_sin2theta)

	print
	printTheoreticalValues()
