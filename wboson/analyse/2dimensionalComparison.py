#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import * # own functions
from tools import randomName
import Styles # official cms-style
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
	'''
	variable: should be 'mwt:el_et' or 'met:el_et', for others borders are not defined
	cut: cutstring
	drawLines: boolean (cuts defined below are drawn)
	save: boolean (save to pdf)
	'''
	mcTree = readTree( "mc_all_new.root/MCTree" )
	dataTree = readTree( "d0_new.root/MessTree" )

	from ROOT import TCanvas, TLegend,TLine
	can = TCanvas( randomName(), '2d', 1400, 700 )
	if save:
		can.SetBatch()
	can.Divide(2,1)
	can.cd(1)

	# number of bins
	xn = 200
	yn = 200

	# currently only two settings are implemented
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

	# intialize lines
	if drawLines:
		xcut = 30
		ycut = 30
		ratiocut = 1.9
		xline = TLine( xcut, ymin, xcut, ymax )
		yline = TLine( xmin, ycut, xmax, ycut )
		xyline = TLine( xmin, ratiocut * xmin, xmax, ratiocut * xmax)

		for line in ( xline, yline, xyline ):
			line.SetLineWidth(2)
			line.SetLineStyle(9)
			line.SetLineColor(2)

	# draw simulation
	mchist2D = create2DHistoFromTree( mcTree, variable, cut, xn, xmin, xmax, yn, ymin, ymax, title )
	mchist2D.SetTitle('Simulation')
	mchist2D.Draw("colz")
	if drawLines:
		xline.Draw()
		if variable == "met:el_et":
			yline.Draw()
		if variable == "mwt:el_et":
			xyline.Draw()

	# draw data
	can.cd(2)
	datahist2D = create2DHistoFromTree( dataTree, variable, cut, xn, xmin, xmax, yn, ymin, ymax, title )
	datahist2D.SetTitle('Daten')
	datahist2D.Draw("colz")
	if drawLines:
		xline.Draw()
		if variable == "met:el_et":
			yline.Draw()
		if variable == "mwt:el_et":
			xyline.Draw()

	# Output on shell
	print 'Correlation for simulated '+variable+': ', mchist2D.GetCorrelationFactor()
	print 'Correlation for generated '+variable+': ', datahist2D.GetCorrelationFactor()

	if save:
		from re import sub
		can.SaveAs('correlation_' + sub(':','VS',variable) + sub( '\.', "_",sub('/',"_",cut)) + '.pdf')
	else:
		can.Update()
		raw_input()
	can.Close()


# entry point
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-c", "--cut", dest="cut", default="", help="Cuts applied to all structures" )
parser.add_argument("-p", "--plots", default="mwt:el_et" )
parser.add_argument("-l", "--drawLines", action = "store_true", default=False )
parser.add_argument("--save", action = "store_true", default=False )
opts = parser.parse_args()

plot2D( opts.plots, opts.cut, opts.drawLines, opts.save )

