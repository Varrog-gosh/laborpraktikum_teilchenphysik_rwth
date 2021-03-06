#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import ROOT
import numpy
from math import *


def extendTree( filename, treename, correction_et = 0 ,correction_met = 0):
	'''
	add certain variables to tree and save in a new file
	filename: input filename, outputFilename will be oldfile_new.root
	treename: treename of file, will not be changed
	correction_et/met: energy correction in %, eg. 2 or -2

	output: void
	'''
	oldfile = ROOT.TFile( filename, "update" )
	oldtree = oldfile.Get( treename )
	nameEnding = '_new.root'
	if correction_et != 0:
		nameEnding = '_et' + str(correction_et) + nameEnding
	if correction_met != 0:
		nameEnding = '_met' + str(correction_met) + nameEnding
	newfile = ROOT.TFile( filename.split('.')[0] + nameEnding, "recreate")
	# clone tree
	newtree = oldtree.CloneTree(0)

	# define arrays to have a referenz equivivalent in python
	met = numpy.zeros(1, dtype=float)
	et = numpy.zeros(1, dtype=float)
	mwt = numpy.zeros(1, dtype=float)
	# Boolean variable to seperate W->e+v from W->tau+v in MC Data
	isTau = numpy.zeros(1, dtype=float)

	# set branch adresses
	newtree.Branch('met', met, 'met/D')
	newtree.Branch('el_et', et, 'el_et/D')
	newtree.Branch('mwt', mwt, 'mwt/D')
	newtree.Branch('isTau', isTau, 'isTau/D')

	nEntries =  oldtree.GetEntries()
	print nEntries
	for i in xrange( nEntries ):
		oldtree.GetEntry(i)
		et[0] = oldtree.el_e * sin( 2*atan( exp( - oldtree.el_eta ) ) ) * ( 1 + 1.* correction_et / 100 )# corrections in %
		met[0] = numpy.sqrt( oldtree.metx_calo**2 + oldtree.mety_calo**2 ) * ( 1 + 1.* correction_met/100 )
		mwt[0] = numpy.sqrt( 2.0 * met[0] * et[0] * ( 1 - numpy.cos( oldtree.el_met_calo_dphi ) ) )
		newtree.Fill()

		if i < 382348:
			isTau[0] = 0
		else :
			isTau[0] = 1

	# save and close
	newtree.AutoSave()
	oldfile.Close()
	newfile.Close()

# computes new trees
extendTree( "d0.root", "MessTree",  0,  0 )
extendTree( "d0.root", "MessTree",  2,  0 ) # et up
extendTree( "d0.root", "MessTree", -2,  0 ) # et down
extendTree( "d0.root", "MessTree",  0,  2 ) # met up
extendTree( "d0.root", "MessTree",  0, -2 ) # met down

extendTree( "mc_all.root", "MCTree" )
