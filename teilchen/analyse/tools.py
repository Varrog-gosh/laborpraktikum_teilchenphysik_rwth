#!/usr/bin/python
# coding=utf8

def printError ( value, error ):
	'''
	Prints error in a nice semiscientific way
	'''
	exponent = int ( format ( error, 'e').split('e')[1] ) - 1
	exponent_val = int ( format ( value, 'e').split('e')[1] )
	value = float ( round ( value / 10**exponent ) ) * 10**exponent
	error = float ( round ( error / 10**exponent ) ) * 10**exponent
	if exponent_val == 0 or exponent_val == 1 or exponent_val == -1:
		print ( "{0} ± {1}".format ( value, error ) )
	else:
		print ( "( {0} ± {1} ) \cdot 10^{2}".format ( value/10**exponent_val, error/10**exponent_val, exponent_val ) )

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

	def __init__( self, xlist, ylist ):
		from ROOT import TGraph
		import numpy
		length = len(xlist)
		self.x = numpy.array( xlist )
		self.y = numpy.array( ylist )
		self.graph = TGraph( length, self.x, self.y )
		self.graph.Fit('pol1')

	def __init__( self, xlist, ylist, exlist, eylist ):
		from ROOT import TGraph, TGraphErrors
		from numpy import array
		length = len(xlist)
		self.x = array( xlist )
		self.y = array( ylist )
		self.ex =array( exlist )
		self.ey = array( eylist )
		self.graph = TGraphErrors( length, self.x, self.y, self.ex, self.ey )
		self.graph.Fit('pol1')

	def residuals(self):
		func = self.graph.GetFunction("pol1")
		for i in range( len( self.x ) ):
			print func.Eval(self.x[i])

a = readFile('testfile')
x = linearRegression(a[0], a[1], [.2,.3,.4,0.1],[1,1,1,0.5])
x.graph.Draw("ap")
x.residuals()

