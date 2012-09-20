#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def drawTau (mcTree,dataTree,variable,cut,nBins):
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	mcTau = createHistoFromTree(mcTree, variable,"isTau && %s"%cut, nBins, xlow, xhigh )
	mcE = createHistoFromTree(mcTree, variable,"!isTau && %s"%cut, nBins, xlow, xhigh )
	dataHisto = createHistoFromTree( dataTree, variable, cut, nBins, xlow, xhigh )
	for entry in [ mcE, mcTau ]:
		entry.Scale( 0.9 / 1164699 * 198 * 2580 )
	print "Number of W->eν events: %d"%mcE.GetEntries()
	print "Number of W->τν events: %d"%mcTau.GetEntries()
	print "Ratio: ", 1.* mcTau.GetEntries() / mcE.GetEntries()
	from ROOT import TCanvas,THStack
	stack = THStack ("stack","W#rightarrowe#nu")
	c = TCanvas()
	c.SetLogy()
	c.cd()

	mcE.SetFillColor(0)
	mcE.SetTitle( title )
	mcTau.SetFillColor(4)
	stack.Add(mcTau,"hist")
	stack.Add(mcE,"hist")
	stack.SetTitle(settings[variable]["title"] )
	stack.SetMinimum(1)
	stack.Draw()
	dataHisto.Draw("sameP")
	raw_input()
	c.Close()

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

	for variable in opts.plots:
		drawTau(mcTree,dataTree,variable,opts.cut,100)
