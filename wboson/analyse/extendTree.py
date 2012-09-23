#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import ROOT
import numpy
from math import *


def extendTree( filename, treename, correction = 0 ):
	'''
	add certain variables to tree and save in a new file
	filename: input filename, outputFilename will be oldfile_new.root
	treename: treename of file, will not be changed
	output: void
	'''
	oldfile = ROOT.TFile( filename, "update" )
	oldtree = oldfile.Get( treename )
	nameEnding = '_new.root'
	if correction != 0:
		nameEnding = '_new' + str(correction) + '.root'
	newfile = ROOT.TFile( filename.split('.')[0] + nameEnding, "recreate")
	# clone tree
	newtree = oldtree.CloneTree(0)

	# define arrays to have a referenz equivivalent in python
	dz = numpy.zeros(1, dtype=float)
	met = numpy.zeros(1, dtype=float)
	et = numpy.zeros(1, dtype=float)
	mwt = numpy.zeros(1, dtype=float)
	# Boolean variable to seperate W->e+v from W->tau+v in MC Data
	isTau = numpy.zeros(1, dtype=float)

	# set branch adresses
	newtree.Branch('dz', dz, 'dz/D')
	newtree.Branch('met', met, 'met/D')
	newtree.Branch('el_et', et, 'el_et/D')
	newtree.Branch('mwt', mwt, 'mwt/D')
	newtree.Branch('isTau', isTau, 'isTau/D')

	nEntries =  oldtree.GetEntries()
	print nEntries
	for i in xrange( nEntries ):
		oldtree.GetEntry(i)
		dz[0] = abs( oldtree.el_track_z - oldtree.met_vertex_z )
		#et[0] = numpy.sqrt( (oldtree.el_px**2 + oldtree.el_py**2) ) # same variable as below, only not sure what is used
		et[0] = oldtree.el_e * sin( 2*atan( exp( - oldtree.el_eta ) ) ) * ( 1 + 1.* correction / 100 )# corrections in %
		met[0] = numpy.sqrt( oldtree.metx_calo**2 + oldtree.mety_calo**2 ) * ( 1 + 1.* correction/100 )
		mwt[0] = numpy.sqrt( 2.0 * met[0] * et[0] * ( 1 - numpy.cos( oldtree.el_met_calo_dphi ) ) )
		newtree.Fill()

		if i < 382348:
			isTau[0] = 0
		else :
			isTau[0] = 1

		# output to see working flow
		#if i%10000000:
			#print int( 100. * i / nEntries )

	# save and close
	newtree.AutoSave()
	oldfile.Close()
	newfile.Close()

extendTree( "d0.root", "MessTree" )
extendTree( "d0.root", "MessTree", 2 )
extendTree( "d0.root", "MessTree", -2 )
extendTree( "mc_all.root", "MCTree" )
extendTree( "mc_all.root", "MCTree" , -2) # energy correction in %
extendTree( "mc_all.root", "MCTree" , 2)
