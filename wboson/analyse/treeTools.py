#! /usr/bin/env python2
# -*- coding: utf-8 -*-

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
		histo.SetTitle(";mass [GeV];Eintr#ddot{a}ge")
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
			"mwt": { "title": ";M_{T} [GeV];Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 250 },
			"met": { "title": ";#slash{E}_{T} [GeV];Eintr#ddot{a}ge",
					"xmin": 5,
					"xmax": 100 },
			"el_et": { "title": ";E_{T} [GeV];Eintr#ddot{a}ge",
					"xmin": 9,
					"xmax": 120},
			"el_eta": { "title": ";#eta;Eintr#ddot{a}ge",
					"xmin": -1.5,
					"xmax": 1.5},
			"el_phi": { "title": ";#phi;Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 6.4},
			"el_iso": {"title": ";electron isolation;Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 0.21},
			"el_met_calo_dphi": {"title": ";#Delta #phi;Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 3.2},
			"el_e": { "title": ";E_{e} [GeV];Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 150},
			"dz": { "title": ";#Delta z [cm];Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 100},
			"el_iso": { "title": ";isolation;Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 0.2},
			"el_emf":{ "title": ";Fraction of Energy in Calorimeter;Eintr#ddot{a}ge",
					"xmin": 0.96,
					"xmax": 1},
			"mwt/el_et":{ "title": ";M_{T}/E_{T};Eintr#ddot{a}ge",
					"xmin": 0,
					"xmax": 3.5}
			}

def prettifySelection(selection):
	from re import sub,match
	replacements = {
			'met': '#slash{E}_{T}',
			'el_et': 'E_{T}',
			'mwt': 'M_{T}',
			'el_iso': 'iso',
			'\s*&&\s*': ', '
			}
	for ugly, nice in replacements.iteritems():
		selection = sub( ugly, nice, selection )
	try:
		massindex, cut  = match( 'weight\[(\d{1,2})\]\s*\*\s*\((.*)\)', selection ).groups()
		selection = cut + ' Generated with ' + str( weightToMass()[int(massindex)] ) + 'GeV'
	except:
		pass
	return selection


