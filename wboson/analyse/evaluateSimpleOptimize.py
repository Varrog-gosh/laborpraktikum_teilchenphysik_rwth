#! /usr/bin/env python2
# -*- coding: utf-8 -*-

###########################################################

# this simple script evaluates the data generated with simpleOptimize.py
# and draws a 2d plot

###########################################################

from treeTools import *
from tools import *

data = readFile('chi2minimization.dat')
import ROOT

xmin = min( data[0] ) -0.5
xmax = max( data[0] ) +0.5
ymin = min( data[1] ) - 0.5
ymax = max( data[1] ) + 0.5
nx = xmax - xmin
ny = ymax - ymin
from math import sqrt
nx = data[0].count( data[0][0] )
ny = data[1].count( data[1][0] )
xmin = 14.5
xmax = 45.5
nx = int(xmax -xmin)
ymin = xmin
ymax = xmax
ny = nx

h = ROOT.TH2D('blub', "name", nx, xmin, xmax, ny, ymin, ymax )
for i in range( len(data[0] ) ):
	if data[2][i]  > 0:
		if data[2][i] > 1.5:
			data[2][i] = 1.5
		h.SetBinContent( h.FindBin( data[0][i]), h.FindBin(data[1][i]), data[2][i] )

ROOT.gStyle.SetOptStat(0)
h.SetTitle("#chi^{2}/NDF;#slash{E}_{T} Grenze; E_{T} Grenze")
h.Draw("colz")
raw_input()
