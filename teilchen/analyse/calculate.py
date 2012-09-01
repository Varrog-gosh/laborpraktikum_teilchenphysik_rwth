#!/usr/bin/python
# coding=utf8

from tools import *
from uncertainties import ufloat
from Styles import tdrStyle
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
u_g.append( arrayToUncertainty( [52, 44, 41, 36, 47, 50] ) )
u_g.append( arrayToUncertainty( [86, 91, 101, 85, 82, 92, 88, 107] ) )
u_g.append( arrayToUncertainty( [174, 167, 163, 170, 169, 172, 172, 167, 160] ) )
u_g.append( arrayToUncertainty( [230, 227, 228, 235, 230, 223, 225, 229] ) )
u_g.append( arrayToUncertainty( [284, 264, 271, 277, 271, 277, 270, 271, 276] ) )

for u in u_g:
	printError(u, unit = 'V')


d = ufloat( ( 0.00305, 0.00025 ) )# m
g = 9.81 # m/s²

for u in [ u_g[1], u_g[4] ]:
	qm_grav = g * d / u
	printError(qm_grav, unit = 'C/kg')

exit()
#### resonanz ####
## ohne luft ##
w_res = ufloat((5,1))
w = ufloat((30,1))
u_x = ufloat((400,10))
K = 8

qm_res_vak = w_res * w * d**2 / ( 4 *sqrt(2) * K * u_x )
printError( qm_res_vak )

## mit luft ##
#A = ufloat(( 0.0001, 0.00001 ))
# keine ahnung


#### Stabilitätsdiagramm ####

## ohne Luft ##
from numpy import array
uxList = array([700, 800, 900, 1000, 1100, 1200])
ugList = array([36, 68, 127, 162, 250, 375])

uxList_drop = array([1280, 1175, 1070, 905])
uyList_drop = array([79, 68, 50, 44])

x2 = array( [1230, 1140, 1000] )
y2 = array( [115, 100, 85] )

x3 = array( [1200, 1100, 1000] )
y3 = array( [280, 260, 320] )

from uncertainties.unumpy import uarray
x = uarray(( uxList, [10.]*len(uxList)))
y = uarray(( ugList, [10.]*len(ugList)))

#x = 6 * K * x**2 / ( w**2 * d**2 )

reg = linearRegression(x**2, y)
reg.func.SetParNames('a','- #frac{q}{m} [#frac{C}{kg}]')
reg.draw(";12 K U_{x}^{2} / (#Omega^{2} d^{2});U_{g} [V]")







































'''# a typical mass
#e = 1.6e-19
#r = ufloat((30e-6,25e-6))
#m = 4./3*pi*r**3*2700 # kg'''



