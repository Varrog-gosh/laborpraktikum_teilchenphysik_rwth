#!/usr/bin/python
# coding=utf8

def printError( value, error = 0 , unit = ''):
	'''
	Prints error in a nice semiscientific way
	Input: value and error or uncertainties.value
	'''
	not_scientific_exponents = [ -1, 0, 1 ] # 30 looks nicer than 3e1
	valid_digits = 1

	# cast uncertainy in value ± error
	from uncertainties import AffineScalarFunc, Variable
	if type( value ) in [ Variable, AffineScalarFunc ]:
		error = value.std_dev()
		value = value.nominal_value

	exponent = int ( format ( error, 'e').split('e')[1] ) + 1 - valid_digits
	exponent_val = int ( format ( value, 'e').split('e')[1] )
	value = float ( round ( value / 10**exponent ) ) * 10**exponent
	error = float ( round ( error / 10**exponent ) ) * 10**exponent
	if exponent_val in not_scientific_exponents:
		print ( "( {0} ± {1} ) {2} rel. {3}".format ( value, error, unit,float(error/value) ) )
	else:
		print ( "( {0} ± {1} ) \cdot 10^{{{2}}} {3} rel. {4}".format ( value/10**exponent_val, error/10**exponent_val, exponent_val, unit,float(error/value) ) )

def listToUncertainty( values ):
	'''
	values: list of values
	returns ufloat with mean and std of input data
	'''
	from numpy import array
	data = array( values )
	from uncertainties import ufloat
	return ufloat( ( data.mean(), data.std() ) )

def abweichung( x1, x2 ):
	''' calculates the derivations in σ from two values.
	Input are two ufloat variables from the package uncertainties
	Output is a float
	'''
	x = abs( x1 - x2 )
	try:
		return 1. * x.nominal_value / x.std_dev()
	except:
		raise ZeroDivisionError('std == 0')

def readFile( filename ):
	'''
	opens a datafile and returns values in lists
	'''
	f = open( filename )
	text = f.readlines()
	f.close()

	# reject all comments and empty lines
	from re import match, split
	data = []
	for line in range( len(text) ):
		if text[line][0] != '#' and not match('\s', text[line]):
			data.append( split('\s', text[line] )[0:-1] )
	# cast all numbers to float
	for i in range( len( data ) ):
		for j in range( len( data[0] ) ):
			data[i][j] = float( data[i][j] )

	# transpose list
	return map( list, zip( *data ) )

class linearRegression:
	def __init__( self, x, y):
		from uncertainties import unumpy
		self.__x = x
		self.__y = y
		from ROOT import TGraphErrors
		self.graph = TGraphErrors( len(x), unumpy.nominal_values(x), unumpy.nominal_values(y) , unumpy.std_devs(x), unumpy.std_devs(y))
		self.graph.Fit('pol1')
		self.graph.Fit('pol1')
		self.func = self.graph.GetFunction('pol1')

	def residuals(self):
		'''
		usually called by draw()
		calculates residuals
		'''
		from uncertainties import unumpy
		from numpy import array
		from ROOT import TGraphErrors
		residuals = array( range( len( self.__x ) ) ,'float')
		for i in range( len( unumpy.nominal_values(self.__x) ) ):
			residuals[i] = self.func.Eval( unumpy.nominal_values(self.__x)[i] ) - unumpy.nominal_values(self.__y)[i]
		self.resgraph = TGraphErrors( len( self.__x ), unumpy.nominal_values(self.__x), residuals, unumpy.std_devs(self.__x), unumpy.std_devs(self.__y) )

	def draw(self, title):
		'''
		draws regression and residuals in one canvas
		'''
		self.residuals()
		from ROOT import TCanvas, TPad, TLine
		from random import randint
		from sys import maxint

		random_name = randint(0,maxint)
		self.canvas = TCanvas("canvas{}".format( random_name), "Linear Regression", 768, 800)
		hPad = TPad("fitPad{}".format( random_name ), "Fit", 0, 0.2, 1, 1)
		hPad.SetFillStyle(4000)
		hPad.SetBorderSize(0)
		hPad.Draw()
		hPad.cd()
		self.graph.SetTitle( title )
		self.graph.Draw("ap")

		self.canvas.cd()
		residualPad = TPad("resPad{}".format( random_name ), "Residuals", 0, 0, 1, 0.2)
		residualPad.SetFillStyle(4000)
		residualPad.SetFrameFillStyle(4000)
		residualPad.SetBorderSize(0)
		residualPad.Draw()
		residualPad.cd()
		self.resgraph.SetTitle( ';' + title.split(';')[1] + '; residuals' )
		xaxis = self.resgraph.GetXaxis()
		xaxis.SetTitleSize(.15)
		xaxis.SetTitleOffset(.3)
		self.resgraph.GetYaxis().SetTitleSize(.25)
		self.resgraph.GetYaxis().SetTitleOffset(.23)
		self.resgraph.GetYaxis().SetLabelSize(.2)
		self.resgraph.Draw("ap")
		self.line = TLine( xaxis.GetXmin(), 0, xaxis.GetXmax(), 0 )
		self.line.Draw()

