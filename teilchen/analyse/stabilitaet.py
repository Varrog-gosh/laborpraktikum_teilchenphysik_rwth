#!/usr/bin/python
# coding=utf8

import ROOT
from tools import *
from uncertainties import umath
from uncertainties.unumpy import uarray
from Styles import tdrStyle
from numpy import array

#nice looking style
tdrStyle()

#in the batch mode no canvas is drawn
# I use this option for avoiding resolution problems when saving
ROOT.gROOT.SetBatch()

ROOT.gStyle.SetStatX(0.95)
ROOT.gStyle.SetStatY(0.4)
ROOT.gStyle.SetStatW(0.23)
ROOT.gStyle.SetStatH(0.15)
#ROOT.gStyle.SetTitleAlign(21) scheint nicht zu klappen :

class messung:
	def __init__( self, x, y, text, saveAffix):
		from ROOT import TPaveText
		self.x = x
		self.y = y
		self.text = text
		self.saveAffix = saveAffix
		error_ug = 15
		error_ux = 10
		x = uarray(( array( x ), [ error_ug ]*len( x )))
		y = uarray(( array( y ), [ error_ux]*len( y )))
		x = x**2 # * 6 * K  / ( w**2 * d**2 )

		self.reg = linearRegression(x, y)
		label = TPaveText(0.6, 0.66, 0.86, 0.88, "NDC")
		label.AddText( text )
		label.SetFillStyle(0)
		label.SetBorderSize(0)
		label.SetTextAlign(10)
		label.Draw()
		self.reg.func.SetParNames('a','b')
		self.reg.draw("%s;U^{2}_{i} [V^{2}];U_{g} [V]"%text )
		self.reg.canvas.SaveAs('linReg%s.pdf'%saveAffix)


# Messungen Freitag :
messung([1280, 1175, 1070, 905] , [79, 68, 50, 44], 'Attention: only changed vx, not vz or vy, so do NOT use this measurement if not ok.', 'NotUse')
#messung([1280, 1175, 1070, 905] , [79, 68, 50, 44], 'Attention', 'NotUse')

messung( [700, 800, 900, 1000, 1100, 1200],
	[36, 68, 127, 162, 250, 375], '', 'fr2')

messung( [1230, 1140, 1000],
	[115, 100, 85], '', 'fr3' )

messung( [1200, 1100, 1000],
	[280, 260, 320], 'macht keinen sinn, ka was falsch war', 'fr4')

###Messungen  Montag Unsicherheit auf U_i ca. 50V
messung([600, 700, 800,970],
	[222, 350, 450,530], "Omega = 30 Hz p=350-400 mbar", 'mo1')

messung( [700, 920, 1080],
	[230, 425, 530], 'Teilchen bei 530 (U_max) immernoch stabil, Omega = 30 Hz p=400 mbar', 'mo2')

messung( [600, 720, 820],
		[220, 360, 510], 'Omega = 30 Hz p=400 mbar', 'mo3' )

messung( [600, 750, 850],
	[50, 77, 120],
	'Alternativwert 135 für letzte Gleichspannung angegebene Omega = 30 Hz p=400-450 mbar', 'mo4')

messung( [850,750,680,600,510,400],
	[460, 375, 300,220,160,50],
	'Omega = 30 Hz p=400-450 mbar', 'mo5' )




'''
# a typical mass
from math import pi
from uncertainties import ufloat
e = 1.6e-19
r = ufloat((30e-6,25e-6))
m = 4./3*pi*r**3*2700 # kg
print 4e-3*m/e
'''
