#!/usr/bin/python
# coding=utf8

import ROOT
ROOT.gROOT.SetBatch()

from tools import *
from uncertainties import ufloat
from uncertainties import umath
from Styles import tdrStyle
from uncertainties.unumpy import uarray
tdrStyle()
#### Stabilitätsdiagramm ####

## mit luft ##
from numpy import array
stab_mes = []
#Messungen Freitag :
stab_mes.append(
	( [1280, 1175, 1070, 905] ,
	[79, 68, 50, 44])) #Attention: only changed vx, not vz or vy, so do NOT use this measurement if not ok.
stab_mes.append(
	( [700, 800, 900, 1000, 1100, 1200],
	[36, 68, 127, 162, 250, 375] ) )
stab_mes.append(
	( [1230, 1140, 1000],
	[115, 100, 85] ) )
###Messungen  Montag Unsicherheit auf U_i ca. 50V
stab_mes.append(
	( [600, 700, 800,970],     #Omega = 30 Hz p=350-400 mbar
	[222, 350, 450,530] ) ) 
stab_mes.append(
	( [700, 920, 1080],		#Omega = 30 Hz p=400 mbar
	[230, 425, 530] ) )  # Teilchen bei 530 (U'_max) immernoch stabil
stab_mes.append(
	( [600, 720, 820],		#Omega = 30 Hz p=400 mbar
	[220, 360, 510] ) )
stab_mes.append(
	( [600, 750, 850],	#Omega = 30 Hz p=400-450 mbar
	[50, 77, 120] ) ) # Alternativwert 135 für letzte Gleichspannung angegebene
stab_mes.append(
	( [850,750,680,600,510,400], #Omega = 30 Hz p=400-450 mbar
	[460, 375, 300,220,160,50] ) )
### Dumpmessung Freitag
stab_mes.append(
	( [1200, 1100, 1000],
	[280, 260, 320] ) )

regs = []
for i in range(len(stab_mes) - 1 ): #last meausurement is corrupted
	x = uarray(( array( stab_mes[i][0] ), [5.]*len( stab_mes[i][0] )))
	y = uarray(( array( stab_mes[i][1] ), [5.]*len( stab_mes[i][0] )))
	x = x**2 # * 6 * K  / ( w**2 * d**2 )

	regs.append(linearRegression(x, y))
	regs[-1].func.SetParNames('a','b')
	regs[-1].draw(";U^{2}_{i} [V^{2}];U_{g} [V]")
	regs[-1].canvas.SaveAs('linReg%s.pdf'%i)







'''# a typical mass
#e = 1.6e-19
#r = ufloat((30e-6,25e-6))
#m = 4./3*pi*r**3*2700 # kg'''

