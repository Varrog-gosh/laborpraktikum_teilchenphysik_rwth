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
	pass
	#printError(u, unit = 'V')


d = ufloat( ( 0.00305, 0.00025 ) )# m
g = 9.81 # m/s²

for u in [ u_g[1], u_g[4] ]:
	qm_grav = g * d / u
	#printError(qm_grav, unit = 'C/kg')

#### resonanz ####
## ohne luft ##
w_res = ufloat((5,1))
w = ufloat((30,1))
u_x = ufloat((400,10))
K = 8
A = 0.0001
u_w = 200
r = d/2

qm_res_vak = w_res * w * d**2 / ( 4 *sqrt(2) * K * u_x )
#PrintError( qm_res_vak )


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


#### Stabilitätsdiagramm ####

## mit luft ##
from numpy import array
x0 = ( [1280, 1175, 1070, 905] ,
	[79, 68, 50, 44]) #Attention: only changed vx, not vz or vy, so do NOT use this measurement if not ok.
x1 = ( [700, 800, 900, 1000, 1100, 1200],
	[36, 68, 127, 162, 250, 375] )
x2 = ( [1230, 1140, 1000],
	[115, 100, 85] )
x3 = ( [1200, 1100, 1000],
	[280, 260, 320] )

regs = []
for messung in [x0, x1, x2, x3]:
	x = uarray(( array( messung[0] ), [10.]*len( messung[0] )))
	y = uarray(( array( messung[1] ), [10.]*len( messung[0] )))
	x = 6 * K * x**2 / ( w**2 * d**2 )

	regs.append(linearRegression(x, y))
	regs[0].func.SetParNames('a','- #frac{q}{m} [#frac{C}{kg}]')
	regs[0].draw(";12 K U_{x}^{2} / (#Omega^{2} d^{2});U_{g} [V]")


## ohne Luft ##






































'''# a typical mass
#e = 1.6e-19
#r = ufloat((30e-6,25e-6))
#m = 4./3*pi*r**3*2700 # kg'''



