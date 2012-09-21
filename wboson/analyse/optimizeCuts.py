#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def efficiency( tree, cut ):
	cuttree = tree.CopyTree( cut )
	return 1. * cuttree.GetEntries() / tree.GetEntries()


def chi2comparison( dataTree, mcTree, cut, variable = 'mwt' ):
	print  cut,
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
	var = chi2min / eff
	print chi2min, eff, var

	del datahist, gr, x, y, func
	# to avoid unphysical values
	if mass < masses[0] or mass > masses[-1]:
		return 1000
	return var

def minimizeChi2( dataTree, mcTree ):
	chi2 = lambda p: chi2comparison( dataTree, mcTree, "met>{} && el_et>{} && mwt/el_et >{}".format( p[0], p[1], p[2]), variable = 'mwt')
	p0 = [ 13.4464975566,20.4083129363,1.60141760266]
	p0 = [ 9.25914050724, 20.4546624238,1.6014176026]
	from scipy import optimize
	cuts = optimize.fmin_powell( chi2, p0 )
	print cuts

mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )

minimizeChi2( dataTree, mcTree)

