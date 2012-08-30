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

#### kompensation der gewichtskraft ######

u_g = ufloat( ( 500, 5 ) )# volt
d = ufloat( ( 3, 0.0003 ) )# m
g = 9.81 # m/s²
e = 1.6e-19

# a typical mass
from math import pi,sqrt
#r = ufloat((30e-6,25e-6))
#m = 4./3*pi*r**3*2700 # kg

qm_grav = g * d /u_g
printError(qm_grav)

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
uxList = array([900.,800.,700.,600.,500.])
ugList = array([400.,325.,260.,185.,120.])
from uncertainties.unumpy import uarray
x = uarray(( uxList, [1.]*len(uxList)))
y = uarray(( ugList, [1.]*len(ugList)))

x = 6 * K * x**2 / ( w**2 * d**2 )

reg = linearRegression(x, y)
reg.func.SetParNames('a','b')
reg.draw(";12 K U_{x}^{2} / (#Omega^{2} d^{2});U_{g} [V]")










































