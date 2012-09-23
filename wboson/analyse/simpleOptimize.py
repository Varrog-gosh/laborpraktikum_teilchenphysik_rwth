#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def chi2comparison( dataTree, mcTree, cut, variable ):
	nBins = 100
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

	# to avoid unphysical values
	del datahist, gr, x, y, func
	return chi2min


def minimizeChi2( dataTree, mcTree ):
	f = open('chi2minimization.dat', "w")
	for met in range( 15, 46, 1):
		for et in range(15, 46, 1):
			x = chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( met, et ), 'mwt' )
			f.write( str(met) + ' ' + str( et ) + ' ' + str(x) + '\n' )
	f.close()


mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )

minimizeChi2( dataTree, mcTree)


