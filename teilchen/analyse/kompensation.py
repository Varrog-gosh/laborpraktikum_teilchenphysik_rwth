#!/usr/bin/python
# coding=utf8

from tools import *
from uncertainties import ufloat
from uncertainties import umath
from Styles import tdrStyle
from uncertainties.unumpy import uarray
tdrStyle()
def abweichung( x1, x2 ):
	''' calculates the derivations in σ from two values.
	Input are two ufloat variables from the package uncertainties
	Output is a float
	'''
	x = abs( x1 - x2 )
	try:
		return 1. * x.nominal_value / x.std_dev()
	except:
		return 0

def longBeta(a, q):
	from uncertainties.umath import sqrt
	return 1.*sqrt( a - (a-1)*q**2 / (2*(a-1)**2-q**2) - (5*a+7)*q**4 / (32*(a-1)**3*(a-4)) - (9*a**2+58*a+29)*q**6 / (64*(a-1)**5*(a-4)*(a-9) ) )

def shortBeta(a,q):
	from uncertainties.umath import sqrt
	return 1.*sqrt(a+q**2/2)

def arrayToUncertainty( values ):
	'''
	values: list of values
	returns ufloat with mean and std of input data
	'''
	from numpy import array
	data = array( values )
	from uncertainties import ufloat
	return ufloat( ( data.mean(), data.std() ) )


#### kompensation der gewichtskraft ######

from math import pi,sqrt
from numpy import array
from sys import exit
u_g = []
u_g.append( arrayToUncertainty( [52, 44, 41, 36, 47, 50] ) ) # 3,4 bewegen sich
u_g.append( arrayToUncertainty( [86, 91, 101, 85, 82, 92, 88, 107] ) ) # 3 still, 4 bewegt sich
u_g.append( arrayToUncertainty( [174, 167, 163, 170, 169, 172, 172, 167, 160] ) ) # 3,4 bewegen sich
u_g.append( arrayToUncertainty( [230, 227, 228, 235, 230, 223, 225, 229] ) ) # 3+4 bewegen sich
u_g.append( arrayToUncertainty( [284, 264, 271, 277, 271, 277, 270, 271, 276] ) ) # 3 droppt, 4 erst kaum bewegung, dann dropp es auch

for u in u_g:
	printError(u, unit = 'V')

d = ufloat( ( 0.00305, 0.00025 ) )# m
g = 9.81 # m/s²

for u in [ u_g[1], u_g[4] ]:
	qm_grav = g * d / u
	printError(qm_grav, unit = 'C/kg')

