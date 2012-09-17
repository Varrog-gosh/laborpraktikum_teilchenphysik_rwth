#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from Styles import tdrStyle
tdrStyle()

from treeTools import *

def drawMCMass( tree, list ):
	masses = weightToMass()
	from ROOT import TCanvas,TLegend
	can = TCanvas()
	can.cd()
	can.SetCanvasSize(1400, 800)
	leg = TLegend(.8,.6,.95,.9)
	leg.SetBorderSize(0)
	leg.SetFillColor(0)
	leg.SetShadowColor(0)
	histlist = []
	niceColors = [1,2,4,6,9,12,46]
	for colorindex, massindex in enumerate( list ):
		histo = createHistoFromTree(tree, "mc_w_m", "weight[{}]".format(massindex), 100, 75, 85)
		histo.SetTitle(";M_{W} [GeV];Eintr#ddot{a}ge")
		histo.SetLineColor( niceColors[colorindex] )
		histo.SetLineWidth(3)
		if histlist == []:
			histo.Draw("hist")
		else:
			histo.Draw("hist,same")
		histlist.append( histo )
		leg.AddEntry(histo, "{0} GeV".format(masses[massindex]), "l")
	leg.Draw()
	can.SaveAs('diffenentMcMasses.pdf')
	can.Close()

drawMCMass( readTree( "mc_all_new.root/MCTree" ) , [0,9,18] )
