#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *
from tools import randomName
import Styles
style = Styles.tdrStyle()
style.SetPadRightMargin(0.1)
style.SetOptTitle()

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
	result.SetTitle(';E_{T} [GeV];M_{T} [GeV]     ')
	return result

def plot2D( cut ):
	mcTree = readTree( "mc_all_new.root/MCTree" )
	dataTree = readTree( "d0_new.root/MessTree" )

	from ROOT import TCanvas, TLegend
	can = TCanvas( randomName(), '2d', 800, 1000 )
	can.SetBatch()
	can.Divide(1,2)
	can.cd(1)
	xn = 200
	xmin = 10
	xmax = 70
	yn = 200
	ymin = 0
	ymax = 100
	mchist2D = create2DHistoFromTree( mcTree, "mwt:el_et", cut, xn, xmin, xmax, yn, ymin, ymax)
	mchist2D.SetTitle('Simulation')
	print mchist2D.GetCorrelationFactor()
	datahist2D = create2DHistoFromTree( dataTree, "mwt:el_et", cut, xn, xmin, xmax, yn, ymin, ymax)
	print datahist2D.GetCorrelationFactor()
	datahist2D.SetTitle('Daten')
	mchist2D.Draw("colz")
	can.cd(2)
	datahist2D.Draw("colz")
	from re import sub
	can.SaveAs('correlation' + sub( '\.', "_",sub('/',"_",cut)) + '.pdf')
	can.Close()

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-c", "--cut", dest="cut", default="", help="Cuts applied to all structures" )
opts = parser.parse_args()

plot2D( opts.cut )

