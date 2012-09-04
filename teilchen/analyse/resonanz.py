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
d = ufloat( ( 0.00305, 0.00025 ) )# m
w_res = ufloat((5,1))
w = ufloat((30,1))
u_x = ufloat((400,10))
K = 8
A = 0.0001
u_w = 200
r = d/2


qm_res_vak = w_res * w * d**2 / ( 4 *sqrt(2) * K * u_x )
#PrintError( qm_res_vak )

##Rauschmessungen U_W Montag
U_W1 = arrayToUncertainty( [ 159,151,153,199,130,201,151,170,130,150190,160 ] )
U_W2 = arrayToUncertainty( [120,160,110,160,170,170,140,140,130,120,140,130] )

for u in [U_W1,U_W2]:
	printError(u, unit = 'V')



## mit luft ##
def qm_res():
	'''
	solves the quadritic formular to compute q/m in air
	the list can obtain up to 2 values, depending on the discriminant of the quadratic formular
	'''
	diskriminant = (u_w*r*w)**4 - 4*(4*K*u_x*A*w_res)**4
	if diskriminant < 0:
		return []
	x1 = ( 4*u_w**2*r**6*w**4 + 4*r**4*w**2 * umath.sqrt( diskriminant ) ) / (128*A**2*(K*u_x)**4)
	x2 = ( 4*u_w**2*r**6*w**4 - 4*r**4*w**2 * umath.sqrt( diskriminant ) ) / (128*A**2*(K*u_x)**4)
	result = []
	for x in [x1, x2]:
		if x > 0:
			result.append( umath.sqrt(x) )
	return result

#for qm in qm_res():
#	printError( qm )


