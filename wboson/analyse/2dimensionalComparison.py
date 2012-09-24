#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *
from tools import randomName
import Styles
style = Styles.tdrStyle()
style.SetPadRightMargin(0.1)
style.SetOptTitle()

def create2DHistoFromTree(tree, variable, weight, nBinsX, xmin, xmax, nBinsY, ymin, ymax, title = '' ):
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
	result.SetTitle( title )
	return result

def plot2D( variable, cut, drawLines, save ):
	mcTree = readTree( "mc_all_new.root/MCTree" )
	dataTree = readTree( "d0_new.root/MessTree" )

	from ROOT import TCanvas, TLegend,TLine
	can = TCanvas( randomName(), '2d', 1400, 700 )
	if save:
		can.SetBatch()
	can.Divide(2,1)
	can.cd(1)
	xn = 200
	yn = 200
	
	line1 = TLine()
	line2 = TLine()
	for line in (line1,line2):
		line.SetLineWidth(2)
		line.SetLineStyle(9)
		line.SetLineColor(2)
		
	if variable == 'mwt:el_et':
		xmin = 10
		xmax = 70
		ymin = 0
		ymax = 100
		title = ';E_{T} [GeV];M_{T} [GeV]     '
	if variable == 'met:el_et':
		xmin = 9
		xmax = 80
		ymin = 9
		ymax = 80
		title = ';E_{T} [GeV];#slash{E}_{T} [GeV]     '
	mchist2D = create2DHistoFromTree( mcTree, variable, cut, xn, xmin, xmax, yn, ymin, ymax, title )
	mchist2D.SetTitle('Simulation')
	print mchist2D.GetCorrelationFactor()
	datahist2D = create2DHistoFromTree( dataTree, variable, cut, xn, xmin, xmax, yn, ymin, ymax, title )
	print datahist2D.GetCorrelationFactor()
	datahist2D.SetTitle('Daten')
	mchist2D.Draw("colz")
	if drawLines:
		line1.DrawLine(30,11,30,78)
		line2.DrawLine(11,30,78,30)
	can.cd(2)
	datahist2D.Draw("colz")

	if drawLines:
		line1.DrawLine(30,11,30,78)
		line2.DrawLine(11,30,78,30)
	if save:
		from re import sub
		can.SaveAs('correlation_' + sub(':','VS',variable) + sub( '\.', "_",sub('/',"_",cut)) + '.pdf')
	else:
		can.Update()
		raw_input()
	can.Close()

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-c", "--cut", dest="cut", default="", help="Cuts applied to all structures" )
parser.add_argument("-p", "--plots", default="mwt:el_et" )
parser.add_argument("-l", "--drawLines", action = "store_true", default=False )
parser.add_argument("--save", action = "store_true", default=False )
opts = parser.parse_args()

plot2D( opts.plots, opts.cut, opts.drawLines, opts.save )

