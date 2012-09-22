#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def drawTau(mcTree, dataTree, variable, cut, save = False, logmode = True, cutline = "NONE", nBins = 100 ):
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]

	# create histograms
	mcTau = createHistoFromTree(mcTree, variable,'weight[9] * (isTau && '+cut+')', nBins, xlow, xhigh )
	mcE = createHistoFromTree(mcTree, variable,"!isTau && %s"%cut, nBins, xlow, xhigh )
	dataHisto = createHistoFromTree( dataTree, variable, cut, nBins, xlow, xhigh )
	for entry in [ mcE, mcTau ]:
		entry.Scale( 0.9 / 1164699 * 198 * 2580 )
	print "Number of W->eν events: %d"%mcE.GetEntries()
	print "Number of W->τν events: %d"%mcTau.GetEntries()
	print "Ratio: ", 1.* mcTau.GetEntries() / mcE.GetEntries()

	from ROOT import TCanvas,THStack, TPaveText, TLegend, TLine
	stack = THStack ("stack","W#rightarrowe#nu")
	c = TCanvas( variable, variable, 1400, 800 )
	if logmode:
		c.SetLogy()
	if save:
		c.SetBatch()
	c.cd()

	mcE.SetFillColor(0)
	mcE.SetTitle( title )
	mcTau.SetFillColor(4)
	stack.Add(mcTau,"hist")
	stack.Add(mcE,"hist")
	stack.SetTitle( title )
	stack.SetMinimum(1)
	stack.Draw()
	dataHisto.Draw("sameP")

	# print cuts in box
	if cut != '1':
		text = TPaveText(0.2, 0.9, .8, 1, 'ndc')
		text.SetFillStyle(0)
		text.SetBorderSize(0)
		text.AddText( prettifySelection( cut ) )
		text.Draw()

	# add legend
	leg = TLegend( .8, .8, 1, 1)
	leg.SetFillColor(0)
	leg.SetBorderSize(0)
	leg.AddEntry( mcTau, "W #rightarrow #tau#nu#nu#nu", "f" )
	leg.AddEntry( mcE, "W #rightarrow e#nu", "l" )
	leg.AddEntry( dataHisto, "Daten", "lp" )
	leg.Draw()

	# draw line
	try:
		x = float( cutline )
		line = TLine( x, stack.GetMinimum(), x, 1.5 * stack.GetMaximum())
		line.SetLineColor(2)
		line.SetLineWidth(2)
		line.SetLineStyle(9)
		line.Draw()
	except:
		pass

	if save:
		c.SaveAs( variable + cut + 'tau.pdf')
	else:
		raw_input()
	c.Close()

if (__name__ == "__main__"):
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("-m", "--mcfile", dest="mcfile", default="mc_all_new.root/MCTree", help="MC file path")
	parser.add_argument("-d", "--datafile", dest="datafile", default="d0_new.root/MessTree", help="Data file path")
	parser.add_argument("-c", "--cut", dest="cut", default="1", help="Cuts applied to all structures" )
	parser.add_argument("-l", "--logarithmic", action="store_true", default=True, help="Plot all distributions in logarithmic mode")
	parser.add_argument("-s", "--save", action="store_true", default=False, help="Plots are not drawn, but saved as pdf")
	parser.add_argument("-p", "--plots", dest="plots", default=['met', 'el_et','mwt'], nargs ="+", help="Distribution which should be plotted")
	parser.add_argument("--cutline", default = 'NONE', help="Draw line to print")

	opts = parser.parse_args()
	import Styles # official cms style
	style = Styles.tdrStyle()
	mcTree = readTree( opts.mcfile )
	dataTree = readTree( opts.datafile )
	if "all" in opts.plots:
		opts.plots = histo_settings().keys()

	for variable in opts.plots:
		drawTau( mcTree, dataTree, variable, opts.cut, opts.save, opts.logarithmic, opts.cutline )
