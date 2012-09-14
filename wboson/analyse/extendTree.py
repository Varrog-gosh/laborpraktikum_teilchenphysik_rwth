#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import ROOT
import numpy


def extendTree( filename, treename ):
	oldfile = ROOT.TFile( filename, "update" )
	oldtree = oldfile.Get( treename )

	dz = numpy.zeros(1, dtype=float)
	met = numpy.zeros(1, dtype=float)
	et = numpy.zeros(1, dtype=float)
	cpurity = numpy.zeros(1, dtype=float)
	mwt = numpy.zeros(1, dtype=float)

	newfile = ROOT.TFile( filename.split('.')[0] + '_new.root', "recreate")
	newtree = oldtree.CloneTree(0)
	newtree.Branch('dz', dz, 'dz/D')
	newtree.Branch('met', met, 'met/D')
	newtree.Branch('et', et, 'et/D')
	newtree.Branch('cpurity', cpurity, 'cpurity/I')
	newtree.Branch('mwt', mwt, 'mwt/D')


	nEntries =  oldtree.GetEntries()
	for i in xrange( nEntries ):
		oldtree.GetEntry(i)

		dz[0] = abs( oldtree.el_track_z - oldtree.met_vertex_z )
		met[0] = numpy.sqrt( oldtree.metx_calo**2 + oldtree.mety_calo**2 )
		et[0] = numpy.sqrt( (oldtree.el_px**2 + oldtree.el_py**2)/(oldtree.el_px**2 + oldtree.el_py**2 + oldtree.el_pz**2) ) * oldtree.el_e
		cpurity[0] = oldtree.el_charge * oldtree.el_track_charge
		mwt[0] = numpy.sqrt( 2.0 * met[0] * et[0] * ( 1 - numpy.cos( oldtree.el_met_calo_dphi ) ) )

		newtree.Fill()
		if i%1000000:
			print int( 100. * i / nEntries )
	newtree.AutoSave()
	oldfile.Close()
	newfile.Close()

extendTree( "d0.root", "MessTree" )
#extendTree( "mc_all.root", "MCTree" )



