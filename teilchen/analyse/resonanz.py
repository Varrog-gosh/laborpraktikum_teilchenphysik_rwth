#!/usr/bin/python
# coding=utf8

from tools import *
from math import pi, sqrt
from uncertainties import ufloat
from uncertainties import umath
from Styles import tdrStyle
from uncertainties.unumpy import uarray
tdrStyle()

d = ufloat( ( 0.0305, 0.002 ) )# plattenabstand in m
f_res = ufloat((5,1)) # resonanzfrequenz für alle versuch in Hz
w_res = 2 * pi * f_res # winkelfrequenz
F = ufloat((30,1)) # fokusierfrequenz
w = 2 * pi * F # winkelfrequenz
V_x = ufloat((400,10)) # u_x = u_y = u…z
u_x = sqrt( 2 ) * V_x # effektive spannung in ampilitude
K = 8 # geometriefaktor
r = d/2

## Bestimmung von A
# bestimmung mit bild vak_falle_teilcen_res.jpg
# innendurchmesser der scheibe * pixelverhältnis von amplitude durch mittlere pixelanzahl scheiben
A = ufloat(( 0.012, 0.005 )) * ufloat(( 0.9, 0.1 )) * 2 / ( ufloat(( 18, 0.1 )) + ufloat(( 15, 0.1 )) )
printError(A)

## Bestimmung der Amplitude der Wecheslspannung
v1 = [ 159,151,153,199,130,201,151,170,130,150,190,160 ] # 160±20
v2 = [ 120,160,110,160,170,170,140,140,130,120,140,130 ] # 140±20
# da die beiden listen mit fehler vereinbar sind, werden die listen als eine betrachtet

# auch hier müssen wir aus der effektiven spannug die amplitude bestimmen
u_w = sqrt(2) * listToUncertainty( v1 + v2  )



#vakuum
qm_res_vak = w_res * w * d**2 / ( 4 *sqrt(2) * K * u_x )

# luft
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

for qm in qm_res():
	printError( qm )

printError( qm_res_vak, unit = 'C / kg' )


