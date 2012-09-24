#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def efficiency( tree, cut ):
	cuttree = tree.CopyTree( cut )
	return 1. * cuttree.GetEntries() / tree.GetEntries()

def settings():
	return { "el_et" : {"xmin": 30, "xmax": 55 },
			"mwt" : {"xmin": 70, "xmax": 95 }
			}

def chi2Test( hist1, hist2 ):
	# histograms with same binning
	minEntry = 10 #minimal events in bin
	ndf = 0
	chi2 = 0
	n1 = hist1.GetNbinsX()
	n2 = hist2.GetNbinsX()
	for ibin in range( 1, nx+1 ):
		if hist1.GetBinContent(ibin) >= minEntry and hist2.GetBinContent(ibin) >= minEntry:
			ndf += 1
			chi2 += ( hist1.GetBinContent(ibin) - hist2.GetBinContent(ibin) )  

mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )


cut = 'met>30 &&el_et>40'
variable = 'el_et'
nBins = 20
firstBin = settings()[variable]["xmin"]
lastBin = settings()[variable]["xmax"]
datahist = createHistoFromTree(dataTree, variable, cut, nBins, firstBin, lastBin)
mchist = createHistoFromTree( mcTree, variable, 'weight[9] * ('+cut+')', nBins, firstBin, lastBin)
mchist.Scale( 1./mchist.Integral() )


def chi2comparison( dataTree, mcTree, cut, variable ):
	print  cut, ':   ',
	nBins = 20
	firstBin = settings()[variable]["xmin"]
	lastBin = settings()[variable]["xmax"]

	datahist = createHistoFromTree(dataTree, variable, cut, nBins, firstBin, lastBin)
	datahist.Scale( 1./datahist.Integral() ) # only form, not amplitude

	from ROOT import TGraph
	from array import array
	x = array('d')
	y = array('d')
	masses = weightToMass()

	for i, mass in enumerate( masses ):
		x.append( mass )
		mchist = createHistoFromTree( mcTree, variable, 'weight['+str(i)+'] * ('+cut+')', nBins, firstBin, lastBin)
		mchist.Scale( 1./mchist.Integral() )
		if i==0:
			mchist.Draw("hist")
			datahist.Draw("same")
			raw_input()

		chi2ndf = datahist.Chi2Test( mchist, "WWchi2/ndf,p") # ndf = nBins + 1, but why?
		y.append( chi2ndf )
		del mchist
	gr = TGraph(len(masses), x,y)
	gr.SetTitle(';M_{W} [GeV];#chi^{2}/NDF')
	gr.Draw("a*")
	gr.Fit('pol2','q')
	func = gr.GetFunction('pol2')
	mass = -func.GetParameter(1) / (2 * func.GetParameter(2))
	chi2min = func.Eval( mass )
	eff = efficiency( mcTree, cut )
	from math import sqrt
	from tools import printError
	printError( mass, sqrt(1. / func.GetParameter(2)) )

	raw_input()
	# to avoid unphysical values
	print chi2min,  eff

	del datahist, gr, x, y, func
	return chi2min


def minimizeChi2( dataTree, mcTree ):
	from scipy import optimize
	variable = 'mwt'
	variable = 'el_et'
	if variable == 'el_et':
		chi2 = lambda p: chi2comparison( dataTree, mcTree, "met>{} && el_et>{} && mwt/el_et >{}".format( p[0], p[1], p[2] ), variable )
		p0 = [ 18, 19.68, 1.7 ]
	if variable == 'mwt':
		chi2 = lambda p: chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( p[0], p[1] ), variable )
		p0 = [ 18.146, 19.68 ]
	cuts = optimize.fmin( chi2, p0, xtol = 1)
	print cuts

mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )

#minimizeChi2( dataTree, mcTree)

#chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( 37, 35 ), "mwt" )
#chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( 40, 39 ), "mwt" )
#chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( 18, 20 ), "mwt" )

