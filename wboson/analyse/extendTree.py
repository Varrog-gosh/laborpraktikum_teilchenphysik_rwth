#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import ROOT
import numpy


def extendTree( filename, treename, calibration = 0 ):
	'''
	add certain variables to tree and save in a new file
	filename: input filename, outputFilename will be oldfile_new.root
	treename: treename of file, will not be changed
	calibration: energy shift, so -0.02 will be an systematic negative error of 2%
	output: void
	'''
	oldfile = ROOT.TFile( filename, "update" )
	oldtree = oldfile.Get( treename )
	if calibration == 0:
		newfile = ROOT.TFile( filename.split('.')[0] + '_new.root', "recreate")
	else:
		newfile = ROOT.TFile( filename.split('.')[0] + str(calibration) + '_new.root', "recreate")
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
	from ROOT import TRandom3
	r = TRandom3()
	for i in xrange( nEntries ):
		oldtree.GetEntry(i)
		dz[0] = abs( oldtree.el_track_z - oldtree.met_vertex_z )
		et[0] = numpy.sqrt( (oldtree.el_px**2 + oldtree.el_py**2) )
		et[0] = r.Gaus(et[0],  calibration * et[0] ) # energy shift if calibration
		met[0] = numpy.sqrt( oldtree.metx_calo**2 + oldtree.mety_calo**2 )
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

#extendTree( "mc_all.root", "MCTree" )
#extendTree( "mc_all.root", "MCTree" )

extendTree( "d0.root", "MessTree", 0.02 )
extendTree( "d0.root", "MessTree", 0.02 )
