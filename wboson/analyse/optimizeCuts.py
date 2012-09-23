#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def efficiency( tree, cut ):
	cuttree = tree.CopyTree( cut )
	return 1. * cuttree.GetEntries() / tree.GetEntries()


def chi2comparison( dataTree, mcTree, cut, variable ):
	print  cut, ':   ',
	nBins = 100
	firstBin = 80
	lastBin = 90
	if variable == 'el_et':
		firstBin  = 30
		lastBin = 55
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
		#mchist.Draw("hist")
		#datahist.Draw("same, hist")
		chi2ndf = datahist.Chi2Test( mchist, "WW,of,uf,chi2/ndf") # ndf = nBins + 1, but why?
		y.append( chi2ndf )
		del mchist
	gr = TGraph(len(masses), x,y)
	gr.SetTitle(';M_{W} [GeV];#chi^{2}/NDF')
	#gr.Draw("ap")
	gr.Fit('pol2','q')
	func = gr.GetFunction('pol2')
	mass = -func.GetParameter(1) / (2 * func.GetParameter(2))
	chi2min = func.Eval( mass )
	eff = efficiency( mcTree, cut )
	print chi2min,  eff
	from math import sqrt
	from tools import printError
	print mass, func.GetParameter(2), func.GetParameter(1), func.GetParameter(0)
	printError( mass, sqrt(1. / func.GetParameter(2)) )

	# to avoid unphysical values
	if mass < masses[0] or mass > masses[-1]:
		chi2min = 3
	if eff < 0.5:
		eff = 0.5

	del datahist, gr, x, y, func
	return chi2min


def minimizeChi2( dataTree, mcTree ):
	from scipy import optimize
	variable = 'mwt'
	variable = 'el_et'
	if variable == 'el_et':
		chi2 = lambda p: chi2comparison( dataTree, mcTree, "met>{} && el_et>{} && mwt/el_et >{}".format( p[0], p[1], p[2] ), variable )
		p0 = [ 20, 20, 1.7 ]
	if variable == 'mwt':
		chi2 = lambda p: chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( p[0], p[1] ), variable )
		p0 = [ 18.146, 19.68 ]
		# p0 = [ 30, 30 ]
	cuts = optimize.fmin( chi2, p0, xtol = 1)
	print cuts

mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )

#minimizeChi2( dataTree, mcTree)

chi2comparison( dataTree, mcTree, "met>30 && el_et>25 &&met/el_et>1.7", "el_et" )
