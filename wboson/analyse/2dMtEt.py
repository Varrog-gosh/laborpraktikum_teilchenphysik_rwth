#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *
def create2DHistoFromTree(tree, variable, weight, nBinsX, xmin, xmax, nBinsY, ymin, ymax ):
	"""
	tree: tree to create histo from
	variable: variable to plot (must be a branch of the tree)
	weight: weights to apply (e.g. "var1*(var2 > 15)" will use weights from var1 and cut on var2 > 15
	nBins, firstBin, lastBin: number of bins, first bin and last bin (same as in TH1F constructor)
	nEvents: number of events to process (-1 = all)
	"""
	from ROOT import TH2D
	from random import randint
	from sys import maxint
	name = "%x"%(randint(0, maxint))
	result = TH2D(name, "", nBinsX, xmin, xmax, nBinsY, ymin, ymax )
	result.Sumw2()
	tree.Draw("%s>>%s"%(variable, name), weight, "colz,goff")
	return result


mcTree = readTree( "mc_all_new.root/MCTree" )
dataTree = readTree( "d0_new.root/MessTree" )
cut = 'mwt/el_et>1.8&&el_et>30 && met > 30'
#cut = ''

from ROOT import TCanvas
can = TCanvas()
can.Divide(1,2)
can.cd(1)
xn = 200
xmin = 10
xmax = 70
yn = 200
ymin = 0
ymax = 100
mchist2D = create2DHistoFromTree( mcTree, "mwt:el_et", cut, xn, xmin, xmax, yn, ymin, ymax)
datahist2D = create2DHistoFromTree( dataTree, "mwt:el_et", cut, xn, xmin, xmax, yn, ymin, ymax)
mchist2D.Draw("colz")
can.cd(2)
datahist2D.Draw("colz")
raw_input()
can.Close()


mchist = createHistoFromTree( mcTree, "mwt/el_et", cut, 200,0,5 )
datahist = createHistoFromTree( dataTree, "mwt/el_et", cut, 200,0,5 )
datahist.Scale( 1./datahist.Integral() )
mchist.Scale( 1./mchist.Integral() )
mchist.SetLineColor(1)

datahist.Draw("hist")
mchist.Draw("same,hist")
