#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def efficiency( tree, cut ):
	cuttree = tree.CopyTree( cut )
	return 1. * cuttree.GetEntries() / tree.GetEntries()


def chi2comparison( dataTree, mcTree, cut, variable = 'mwt' ):
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
		mchist.Draw("hist")
		datahist.Draw("same, hist")
		#raw_input()
		prob = datahist.Chi2Test( mchist, "WW,of,uf")
		y.append( prob )
	gr = TGraph(len(masses), x,y)
	gr.SetTitle(';M_{W} [GeV];prob')
	gr.Draw("ap")
	gr.Fit('pol2','q')
	func = gr.GetFunction('pol2')
	mass = -func.GetParameter(1) / (2 * func.GetParameter(2))
	chi2min = func.Eval( mass )
	print
	print cut
	print 'probability: ', chi2min
	print 'efficiency: ', efficiency( mcTree, cut )
	#datahist.Draw("hist")
	#mchist.Draw("hist, same")
	return chi2min

def minimizeChi2( dataTree, mcTree ):
	chi2 = lambda p: -chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( p[0], p[1]), variable = 'mwt')
	p0 = [40, 40]
	from scipy import optimize
	cuts = optimize.fmin_powell( chi2, p0 , xtol = 5, ftol = 0.1)
	print cuts

mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )


minimizeChi2( dataTree, mcTree)
