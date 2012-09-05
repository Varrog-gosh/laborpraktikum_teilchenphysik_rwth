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

def usysqm (g,d,ed,u,eu):
	return g/u * sqrt(ed**2 + eu**2 * d**2 / u**2) 

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
u_g = [] #V
u_g.append( arrayToUncertainty( [52, 44, 41, 36, 47, 50] ) ) # 3,4 bewegen sich
u_g.append( arrayToUncertainty( [86, 91, 101, 85, 82, 92, 88, 107] ) ) # 3 still, 4 bewegt sich
u_g.append( arrayToUncertainty( [174, 167, 163, 170, 169, 172, 172, 167, 160] ) ) # 3,4 bewegen sich
u_g.append( arrayToUncertainty( [230, 227, 228, 235, 230, 223, 225, 229] ) ) # 3+4 bewegen sich
u_g.append( arrayToUncertainty( [284, 264, 271, 277, 271, 277, 270, 271, 276] ) ) # 3 droppt, 4 erst kaum bewegung, dann dropp es auch
# Ab hier Messungen von Montag
# erste Messung mit selbstgebauter Falle bei Normaldruck Omega = 30Hz U_i = 1000V
u_g.append( arrayToUncertainty( [39,31,32,27,33,41,29,28,36,29] ) ) # wenig Bewegung
u_g.append( arrayToUncertainty( [47,52,55,53,61,48,46,49,44,45,53,52,49] ) )  # still bzw. sehr wenig Bewegung
u_g.append( arrayToUncertainty( [56,62,63,61,65,64,66,51,61,55,53,63] ) )  #  wenig Bewegung (weniger als bei Mesung 1 mehr als bei 2)
u_g.append( arrayToUncertainty( [89,87,93,90,81,87,109,86,97,87,88,99,95] ) )  #  deutliche Bewegung 

#zweite Messung unter "Vakuum" Omega=32Hz U_i = 1000V p=450 mbar
u_g.append( arrayToUncertainty( [23,27,25,24,28,17,30,26,25,28] ) ) #wenig Bewegung
u_g.append( arrayToUncertainty( [66,68,64,70,72,66,69] ) )  #still
u_g.append( arrayToUncertainty( [88,78,82,86,75,72,76,65,84,81] ) ) # wenig  Bewegung

print "test"
print u_g[3]
for u in u_g:
	print u_g
	#~ printError(u, unit = 'V')
	
ug_new = []
ug_new2 = []
for i in [1,6,10]:
	#~ print u_g[i+1] - u_g[i-1]
	diff  = (u_g[i+1] - u_g[i-1])/2
	ug_new.append( [ u_g[i].nominal_value , diff.nominal_value,i] )
	#~ ug_new2.append(  ufloat( u_g[i].nominal_value , diff )
	
print "U_G"
ug_new.reverse()
ug_new.append([273,55,4])
d = ufloat( ( 0.0305, 0.002 ) )# m
g = 9.81 # m/s²


#~ for u in ug:
	 #~ qm_grav = g * d / u
	 #~ printError(qm_grav, unit = 'C/kg')
dval = d.nominal_value
edval = d.std_dev()
print "Messung 1 bei 450mbar"
for i,u in enumerate(ug_new):
	print i+1
	print "U_g: %f +- %f (stat.) +- %f (sys.) V"%(u[0],u_g[u[2]].std_dev(),u[1])
	qm_grav = g * d.nominal_value / u_g[u[2]]
	qm = g * dval / u[0]
	#~ print "uncertain q/m: %e +- %e (stat.) +- %e (sys.) C/kg \n"%(qm,qm_grav.std_dev(),usysqm(g,dval,edval,u[0],u[1]))
	print "byhand q/m: %e +- %e (stat.) +- %e (sys.) C/kg \n"%(qm,usysqm( g,dval,0,u[0],u_g[u[2]].std_dev() ),usysqm( g,dval,edval,u[0],u[1]) )
