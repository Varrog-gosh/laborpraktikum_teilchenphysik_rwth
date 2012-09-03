#!/usr/bin/python
# coding=utf8

from tools import *
from uncertainties import ufloat

d = ufloat( ( 0.00305, 0.0002 ) )# m
g = 9.81 # m/s²

u1 = []
u1.append( listToUncertainty( [52, 44, 41, 36, 47, 50] ) ) # 3,4 bewegen sich
u1.append( listToUncertainty( [86, 91, 101, 85, 82, 92, 88, 107] ) ) # 3 still, 4 bewegt sich
u1.append( listToUncertainty( [174, 167, 163, 170, 169, 172, 172, 167, 160] ) ) # 3,4 bewegen sich
u1.append( listToUncertainty( [230, 227, 228, 235, 230, 223, 225, 229] ) ) # 3+4 bewegen sich
u1.append( listToUncertainty( [284, 264, 271, 277, 271, 277, 270, 271, 276] ) ) # 3 droppt, 4 erst kaum bewegung, dann dropp es auch
u1.append( listToUncertainty( [294, 264, 271, 277, 271, 277, 270, 271, 276] ) ) # not measure, just for testign

still = [ 1, 4 ]

print('spnnungen:')
for u in u1:
	printError(u, unit = 'V')

for i in still:
	delta = (u1[ i-1 ].nominal_value + u1[ i+1 ].nominal_value)/2
	u = ufloat( ( u1[i].nominal_value, delta ) )
	qm_grav = g * d / u
	printError(qm_grav, unit = 'C/kg')

