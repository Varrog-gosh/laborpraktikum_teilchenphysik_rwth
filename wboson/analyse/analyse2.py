#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import ROOT
from ROOT import TTree

from messageLogger import messageLogger as log
from optparse import OptionParser


def totalNumberOfGeneratedEvents(path):
	from ROOT import TFile
	result = {}
	for sampleName, filePath in getFilePathsAndSampleNames(path).iteritems():
		rootFile = TFile(filePath, "read")
		result[sampleName] = rootFile.FindObjectAny("analysis paths").GetBinContent(1)
	return result

def createHistoFromTree(tree, variable, weight, nBins, firstBin, lastBin, nEvents = -1):
	"""
	tree: tree to create histo from
	variable: variable to plot (must be a branch of the tree)
	weight: weights to apply (e.g. "var1*(var2 > 15)" will use weights from var1 and cut on var2 > 15
	nBins, firstBin, lastBin: number of bins, first bin and last bin (same as in TH1F constructor)
	nEvents: number of events to process (-1 = all)
	"""
	from ROOT import TH1F
	from random import randint
	from sys import maxint
	if nEvents < 0:
		nEvents = maxint
	#make a random name you could give something meaningfull here,
	#but that would make this less readable
	name = "%x"%(randint(0, maxint))
	result = TH1F(name, "", nBins, firstBin, lastBin)
	result.Sumw2()
	tree.Draw("%s>>%s"%(variable, name), weight, "goff", nEvents)
	return result

def readTree( filename ):
	from ROOT import TChain
	result = TChain()
	result.Add( filename)
	return result

def weightToMass():
	"""
	returs list with weight[ listindex ] ↦ mass
	"""
	return [ 79.9446, 79.9946, 80.0446, 80.0946, 80.1446, 80.1946, 80.2446, 80.2946, 80.3446, 80.3946,80.4446,80.4946,80.5446,80.5946,80.6446,80.6946,80.7446,80.7946,80.8446]


def drawMCMass( tree, list ):
	masses = weightToMass()
	from ROOT import TCanvas,TLegend
	can = TCanvas()
	leg = TLegend(.7,.5,.95,.9)
	leg.SetBorderSize(0)
	leg.SetFillColor(0)
	leg.SetShadowColor(0)
	histlist = []
	for massindex in list:
		histo = createHistoFromTree(tree, "mc_w_m", "weight[{}]".format(massindex), 100, 75, 85)
		histo.SetTitle(";mass [GeV];Entries")
		histo.SetLineColor( massindex+1 )
		histo.SetLineWidth(3)
		if histlist == []:
			histo.Draw("hist")
		else:
			histo.Draw("hist,same")
		histlist.append( histo )
		leg.AddEntry(histo, "{0} GeV".format(masses[massindex]), "l")
	leg.Draw()
	raw_input()

def histo_settings():
	return {
			"mwt": { "title": ";M^{W}_{T};Entries",
					"xmin": 0,
					"xmax": 250 },
			"met": { "title": ";#slash{E}_{T};Entries",
					"xmin": 5,
					"xmax": 100 },
			"el_et": { "title": ";E_{T};Entries",
					"xmin": 9,
					"xmax": 120},
			"cpurity": { "title": ";charge - charge_{track};Entries",
					"xmin": -2.5,
					"xmax": 2.5},
			"el_eta": { "title": ";#eta;Entries",
					"xmin": -1.5,
					"xmax": 1.5},
			"el_phi": { "title": ";#phi;Entries",
					"xmin": 0,
					"xmax": 6.4},
			"el_iso": {"title": ";electron isolation;Entries",
					"xmin": 0,
					"xmax": 0.2},
			"dz": { "title": ";#Delta z;Entries",
					"xmin": 0,
					"xmax": 7},
			"el_met_calo_dphi": {"title": ";#Delta #phi;Entries",
					"xmin": 0,
					"xmax": 3.2}
			}


def compareDataMC( mcTree, dataTree, variable, cut, nBins = 100 ):
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	mcHisto = createHistoFromTree( mcTree, variable, cut, nBins, xlow, xhigh )
	mcHisto.Scale( 0.9 / 1164699 * 198 * 2580 )
	dataHisto = createHistoFromTree( dataTree, variable, cut, nBins, xlow, xhigh )
	from ROOT import TCanvas
	c = TCanvas()
	c.SetLogy()
	c.cd()
	mcHisto.Draw("hist")
	mcHisto.SetTitle( title )
	dataHisto.Draw("same")
	raw_input()
	c.Close()

if (__name__ == "__main__"):
	from argparse import ArgumentParser
	# use option parser to allow verbose mode
	parser = ArgumentParser()
	parser.add_argument("-n", "--nEvents", dest="nEvents", default="-1", help="number of events to read (default = -1 = all). use smaller numbers for tests")
	parser.add_argument("-m", "--mcfile", dest="mcfile", default="mc_all_new.root/MCTree", help="MC file path")
	parser.add_argument("-d", "--datafile", dest="datafile", default="d0_new.root/MessTree", help="Data file path")
	parser.add_argument("-c", "--cut", dest="cut", default="", help="Cuts applied to all structures" )
	parser.add_argument("-l", "--logarithmic", dest="logarithmic", default=True, help="Plot all distributions in logarithmic mode") #not implemented yet
	parser.add_argument("-s", "--save", dest="save", default=False, help="Plots are not drawn, but saved as pdf") #not implemented yet

	parser.add_argument("-p", "--plots", dest="plots",
			default=['met', 'el_et','mwt'],
			nargs ="+",
			help="Distribution which should be plotted")

	opts = parser.parse_args()
	import Styles # official cms style
	style = Styles.tdrStyle()
	mcTree = readTree( opts.mcfile )
	dataTree = readTree( opts.datafile )

	for variable in opts.plots:
		compareDataMC( mcTree, dataTree, variable, opts.cut)
	#drawMCMass( mcTree, [ 1, 9, 17 ] )


