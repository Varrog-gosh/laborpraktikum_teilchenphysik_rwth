#!/usr/bin/python
# coding=utf8

from uncertainties import ufloat
from tools import printError
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
r = ufloat((30e-6,25e-6))
m = 4./3*pi*r**3*2700 # kg

qm_grav = g * d /u_g / e
printError(qm_grav)

#### resonanz ####
## ohne luft ##
w_res = ufloat((5,1))
w = ufloat((30,1))
u_x = ufloat((400,10))
d = 2 * ufloat((0.02 , 0.001))
K = 8

qm_res_vak = w_res * w * d**2 / ( 4 *sqrt(2) * K * u_x )
print qm_res_vak
