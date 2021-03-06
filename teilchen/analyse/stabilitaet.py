#!/usr/bin/python
# coding=utf8

import ROOT
from tools import *
from math import sqrt
from uncertainties import umath
from uncertainties.unumpy import uarray
from Styles import tdrStyle
from numpy import array
from sys import exit

#nice looking style
tdrStyle()

#in the batch mode no canvas is drawn
# I use this option for avoiding resolution problems when saving
ROOT.gROOT.SetBatch()

ROOT.gStyle.SetStatX(0.95)
ROOT.gStyle.SetStatY(0.4)
ROOT.gStyle.SetStatW(0.23)
ROOT.gStyle.SetStatH(0.15)

class messung:
	def __init__( self, x, y, text, saveAffix, execludeLast = False):
		from ROOT import TPaveText
		self.x = x
		self.y = y
		self.text = text
		self.saveAffix = saveAffix
		error_ug = 15
		error_ux = 10 * sqrt(2)
		x = uarray(( array( x ), [ error_ug ]*len( x )))
		y = uarray(( array( y ), [ error_ux]*len( y )))
		x = x**2

		self.reg = linearRegression(x, y, execludeLast )
		self.reg.func.SetParNames('a','b')
		self.reg.draw(";U^{2}_{i} [V^{2}];U_{g} [V]" )
		self.reg.canvas.cd()
		label = TPaveText(0.1, 0.95, .86, 1, "NDC")
		label.AddText( text )
		label.SetFillStyle(0)
		label.SetBorderSize(0)
		label.Draw()
		ROOT.kPrint = 0
		'''
		ROOT.kInfo = 1000
		ROOT.kWarning = 2000;
		ROOT.kError = 3000;
		ROOT.Break = 4000;
		ROOT.kSysError = 5000;
		ROOT.kFatal = 6000;
		'''
		self.reg.canvas.SaveAs('linReg%s.pdf'%saveAffix)

		# calculate q_m
		# variable definitions:
		from math import pi
		K = 8
		w =  2. * pi * 30
		e_w = 2. * pi
		r =   0.0305 / 2
		e_r = 0.0002 / 2
		#print( '"{}  +/- {}",'.format(self.reg.func.GetParameter(0), self.reg.func.GetParError(0) ) )
		b = self.reg.func.GetParameter(1)
		if b == 0:
			return
		e_b = self.reg.func.GetParError(1)
		q_m = -2. * w**2 * r**2 * b / ( 3 * K ) * 1e6
		stat = abs( 1.* q_m * e_b / b )
		sys = abs (2. * q_m * sqrt( (e_w/w)**2 + (e_r/r)**2 ) )
		#print('{}: q/m = {:.4e} ± {:.2e} (stat) ± {:.2e} (sys) ± {:.2e} (gesamt) μC/kg\n'.format(saveAffix, q_m, stat, sys, sqrt(stat**2 + sys**2)))
		druck = { 'Luft1': 1000, 'Luft2': 1000, '375bar': 375, '400bar': 400, '425bar': 425, '425bar2': 425 }
		print('{} & {:.3g} ± {:.2g} (stat) ± {:.2g} (sys) {:2g}\\\\'.format(druck[saveAffix], -q_m, stat, sys, sqrt( stat**2 + sys**2) ))

print('p [mbar]                         q/m [μC/kg]')

# Messungen Freitag :
#messung([1280, 1175, 1070, 905] , [79, 68, 50, 44], 'Attention: only changed vx, not vz or vy, so do NOT use this measurement if not ok.', 'VxNotVyNotVz')

messung( [700, 800, 900, 1000, 1100, 1200],
	[36, 68, 127, 162, 250, 375],
	'p = 1 bar, Fit ohne letzten Wert', 'Luft1', True)

messung( [1230, 1140, 1000],
	[115, 100, 85], 'p = 1 bar', 'Luft2' )

#messung( [1200, 1100, 1000], [280, 260, 320], 'macht keinen sinn, ka was falsch war', 'LuftKaputt')

###Messungen  Montag Unsicherheit auf U_i ca. 50V
messung([600, 700, 800,970],
	[222, 350, 450,530],
	"p = 0.375 bar, Fit ohne letzten Wert", '375bar', True)

#messung( [700, 920, 1080], [230, 425, 530], 'p = 0.4 bar, letzter Wert nicht im Fit, da max', '400bar2')

messung( [600, 720, 820],
		[220, 360, 510], 'p = 0.4 bar', '400bar' )

messung( [600, 750, 850],
	[50, 77, 120],
	'p = 0.425 bar', '425bar')

messung( [850,750,680,600,510,400],
	[460, 375, 300,220,160,50],
	'p = 0.425 bar', '425bar2' )




# a typical mass
print
from math import pi
from uncertainties import ufloat
e = 1.6e-19
r = ufloat((30e-6,25e-6))/2
m = 4./3*pi*r**3*2700 # kg
printError(m,'kg')
#minimal and maximal ration q/m:
qm1 = 6e-3
qm2 = 4e-5
print 'Charge of patricles:'
printError(qm1*m, unit = 'C')
printError(qm1*m/e, unit = 'e')
printError(qm2*m, unit = 'C')
printError(qm2*m/e, unit = 'e')

