#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from treeTools import *

def compareDataMC( mcTree, dataTree, variable, cut, nBins = 100 ):
	settings = histo_settings()
	xlow = settings[variable]["xmin"]
	xhigh = settings[variable]["xmax"]
	title = settings[variable]["title"]
	mcHisto = createHistoFromTree( mcTree, variable, 'weight[9] * ('+cut+')', nBins, xlow, xhigh )
	mcHisto.Scale( 0.9 / 1164699 * 198 * 2580 )  # 0.9-Korrekturfaktor / 1164699-generated Events / 198 - Lumi / 2580 - xs [pb]
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


def chi2comparison( dataTree, mcTree, cut, variable = 'mwt' ):
	'''
	variable could be el_et later
	'''
	nBins = 50
	firstBin = 50
	lastBin = 100
	datahist = createHistoFromTree(dataTree, variable, cut, nBins, firstBin, lastBin)
	#~ datahist.Scale( 1./datahist.Integral() )
	from ROOT import TGraph
	from array import array
	x = array('d')
	y = array('d')
	masses = weightToMass()
	for i, mass in enumerate( masses ):
		x.append( mass )
		mchist = createHistoFromTree( mcTree, variable, 'weight['+str(i)+'] * ('+cut+')', nBins, firstBin, lastBin)
		#~ mchist.Scale( 1./mchist.Integral() )
		mchist.Scale( 0.9 / 1164699 * 198 * 2580 ) 
		chi2 = datahist.Chi2Test( mchist, "UW,of,uf,chi2/ndf")
		y.append(chi2)
	gr = TGraph(len(masses), x,y)
	gr.SetTitle(';M_{W} [GeV];#chi^{2}/NDF')
	gr.Draw("ap")
	gr.Fit('pol2','q')
	func = gr.GetFunction('pol2')
	mass = -func.GetParameter(1) / (2 * func.GetParameter(2))
	chi2min = func.Eval( mass )
	'''
	offset = 1 # how much χ² should change for error
	from math import sqrt
	try:
		e_mass = sqrt( 1.* offset / func.GetParameter(2) )
	except:
		e_mass = 0
	#print('{} ± {}'.format(mass, e_mass ))
	#raw_input()
	'''
	return chi2min

def efficiency( tree, cut ):
	cuttree = tree.CopyTree( cut )
	return 1. * cuttree.GetEntries() / tree.GetEntries()

def trydifferentCuts(dataTree,mcTree):
	f = open('optimizeM.txt','w')
	for met in range(25,60,5):
		for et in range(25,60,5):
			try:
				cut =  "met>{} && el_et>{}".format(met, et)
				chi2 = chi2comparison( dataTree, mcTree, cut, variable = 'mwt' )
				e = efficiency( mcTree, cut )
				f.write( "{} {} {:2g} {:2g}\n".format( met, et, chi2,e))
			except:
				pass
	f.close()

def minimizeChi2( dataTree, mcTree ):
	chi2 = lambda p: -chi2comparison( dataTree, mcTree, "met>{} && el_et>{}".format( p[0], p[1]), variable = 'mwt')
	p0 = [30,30]
	from scipy import optimize
	cuts = optimize.fmin_powell( chi2, p0, maxiter = 2 )
	print cuts



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

	#~ for variable in opts.plots:
		#~ compareDataMC( mcTree, dataTree, variable, opts.cut)
	#print "The Crosssection is :%e pb"%Get_xs(dataTree,mcTree,opts.plots[0],opts.cut)
	#chi2comparison( dataTree, mcTree, opts.cut, variable = 'mwt' )
	#trydifferentCuts( dataTree, mcTree)
	minimizeChi2( dataTree, mcTree)
