#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def compareDataMC( mcTree, dataTree, variable, cut, save = False, logmode = True, nBins = 100 ):
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	mcHisto = createHistoFromTree( mcTree, variable, 'weight[9] * ('+cut+')', nBins, xlow, xhigh )
	mcHisto.Scale( 0.9 / 1164699 * 198 * 2580 )  # 0.9-Korrekturfaktor / 1164699-generated Events / 198 - Lumi / 2580 - xs [pb]
	dataHisto = createHistoFromTree( dataTree, variable, cut, nBins, xlow, xhigh )
	from ROOT import TCanvas, TPaveText
	c = TCanvas( variable, variable, 1400, 800 )
	if logmode:
		c.SetLogy()
	if save:
		c.SetBatch()
	c.cd()
	mcHisto.Draw("hist")
	mcHisto.SetTitle( title )
	dataHisto.Draw("same")
	if cut != '1':
		text = TPaveText(0.2, 0.8, .9, .9, 'ndc')
		text.SetFillStyle(0)
		text.SetBorderSize(0)
		text.AddText( prettifySelection( cut ) )
		text.Draw()
	if save:
		c.SaveAs( variable + cut + '.pdf')
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

	opts = parser.parse_args()
	import Styles # official cms style
	style = Styles.tdrStyle()
	mcTree = readTree( opts.mcfile )
	dataTree = readTree( opts.datafile )
	if "all" in opts.plots:
		opts.plots = histo_settings().keys()

	for variable in opts.plots:
		compareDataMC( mcTree, dataTree, variable, opts.cut, opts.save, opts.logarithmic)
