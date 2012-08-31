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
	'''
	from numpy import array
	data = array( values )
	from uncertainties import ufloat
	return ufloat( ( data.mean(), data.std() ) )


#### kompensation der gewichtskraft ######

from math import pi,sqrt
from numpy import array
u_g = arrayToUncertainty( [388, 417, 378, 294, 361, 369, 332, 395, 417, 313] )
print 'u_g: ', u_g
u_g = ufloat ( ( 130, 20 ))
d = ufloat( ( 0.00305, 0.00025 ) )# m
g = 9.81 # m/s²
e = 1.6e-19

'''# a typical mass
#r = ufloat((30e-6,25e-6))
#m = 4./3*pi*r**3*2700 # kg'''

qm_grav = g * d /u_g
printError(qm_grav, unit = 'C/kg')

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
uxList = array([1230, 1140, 1000])
ugList = array([115, 100, 85])
from uncertainties.unumpy import uarray
x = uarray(( uxList, [10.]*len(uxList)))
y = uarray(( ugList, [10.]*len(ugList)))

#x = 6 * K * x**2 / ( w**2 * d**2 )

reg = linearRegression(x**2, y)
reg.func.SetParNames('a','- #frac{q}{m} [#frac{C}{kg}]')
reg.draw(";12 K U_{x}^{2} / (#Omega^{2} d^{2});U_{g} [V]")










































