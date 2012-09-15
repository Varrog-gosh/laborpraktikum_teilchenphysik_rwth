#! /usr/bin/env python2
# -*- coding: utf-8 -*-

from treeTools import *

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
	can.Close()

drawMCMass( readTree( "mc_all_new.root/MCTree" ) , [0,9,18] )
