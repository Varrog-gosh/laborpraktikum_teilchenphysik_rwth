#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def Get_xs(dataTree,mcTree,variable,cut):
	#returns crosssection
	#uses efficiency e eff = n_after_cut / n_generated
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	nBins = 10 # default value
	ngen = 1164699
	mcHisto = createHistoFromTree( mcTree, variable, cut, nBins, xlow, xhigh )
	n_after_cut = mcHisto.GetEntries()
	eff = n_after_cut / ngen
	dataHisto = createHistoFromTree( dataTree, variable, cut, nBins, xlow, xhigh )
	n_obs = dataHisto.GetEntries()
	lumi = 198
	corr = 0.9
	xs = n_obs / eff / lumi / corr
	return xs

def getWeinberg (mw,err_mw):
	mz = 91.227
	err_mz = 0.041
	cos_wein = mw / mz
	err_cos_wein = sqrt(err_mw**2 / mz**2 + mw**2 / mz**4 * err_mz**2)
	print "Cos(Theta) = %f +/- %f" % (cos_wein,err_cos_wein)
	return cos_wein,err_con_wein

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

	m = 80
	e_m = 2

	#print "The Crosssection is :%e pb"%Get_xs(dataTree,mcTree,opts.plots[0],opts.cut)
