#!/usr/bin/python
# coding=utf8

def printError( value, error = 0 , unit = '', relative = False ):
	'''
	Prints error in a nice semiscientific way
	Input: value and error or uncertainties.value
	'''
	not_scientific_exponents = [ -1, 0, 1, 2 ] # 30 looks nicer than 3e1
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
	valstring = "( {0} ± {1} )".format( value, error )
	if exponent_val in not_scientific_exponents:
		valstring = valstring + ' ' + unit
	else:
		valstring = "( {0} ± {1} ) \cdot 10^{{{2}}} {3}".format ( value/10**exponent_val, error/10**exponent_val, exponent_val, unit)
	if relative:
		valstring = valstring + ' relative Error: ' + str( 1. * error / value )
	print( valstring )

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
	# cast all numbers to float or int, if possible
	for i in range( len( data ) ):
		for j in range( len( data[0] ) ):
			if data[i][j].isalnum():
				data[i][j] = int( data[i][j] )
			else:
				try:
					data[i][j] = float( data[i][j] )
				except:
					pass

	# transpose list
	return map( list, zip( *data ) )

class linearRegression:
	def __init__( self, x, y, ex, ey, beginning = 0 ):
		from uncertainties import unumpy
		if type( x ) == unumpy.uarray or type( y ) == unumpy.uarray:
			self.__x = unumpy.nominal_values(x)
			self.__y = unumpy.nominal_values(y)
			self.__ex = unumpy.std_devs(x)
			self.__ey = unumpy.std_devs(y)
		else:
			from numpy import array
			self.__x = array(x, dtype = 'd')
			self.__y = array(y, dtype = 'd')
			self.__ex = array(ex, dtype = 'd')
			self.__ey = array(ey, dtype = 'd')

		if len(x) != len(y) != len(ex) != len(ey):
			raise IndexError('All lengths should be the same')
		from ROOT import TGraphErrors, TF1
		self.graph = TGraphErrors( len(self.__x), self.__x, self.__y, self.__ex, self.__ey)
		self.func = TF1('fit', 'pol1', beginning, self.__x[-1] )
		self.graph.Fit('fit', 'QR')


	def residuals(self):
		'''
		usually called by draw()
		calculates residuals
		'''
		from uncertainties import unumpy
		from numpy import array
		from ROOT import TGraphErrors
		residuals = self.__y
		for i in range( len( self.__x ) ):
			residuals[i] = self.__y[i] - self.func.Eval( self.__x[i] )
		self.resgraph = TGraphErrors( len( self.__x ), self.__x, residuals, self.__ex, self.__ey )

	def draw(self, title):
		'''
		draws regression and residuals in one canvas
		'''
		self.residuals()
		from ROOT import TCanvas, TPad, TLine
		from random import randint
		from sys import maxint

		random_name = randint(0,maxint)
		self.canvas = TCanvas("canvas{}".format( random_name), "Linear Regression", 1300, 800)
		self.canvas.SetBatch()
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
		# get y-label for residuals
		from re import match
		try:
			splittitle = title.split(';')
			val, unit = match( '(.*)\[(.*)\]', splittitle[2] ).groups()
			restitle = splittitle[0] + ';' + splittitle[1] + ';' + val + '- fit [' + unit + ']'
			self.resgraph.SetTitle( restitle )
		except:
			self.resgraph.SetTitle( title + ' - fit' )
		xaxis = self.resgraph.GetXaxis()
		xaxis.SetTitleSize(.15)
		xaxis.SetTitleOffset(.3)
		self.resgraph.GetYaxis().SetNdivisions( 8,0 ,0 )
		self.resgraph.GetYaxis().SetTitleSize(.18)
		self.resgraph.GetYaxis().SetTitleOffset(.23)
		self.resgraph.GetYaxis().SetLabelSize(.2)
		self.resgraph.Draw("ap")
		self.line = TLine( xaxis.GetXmin(), 0, xaxis.GetXmax(), 0 )
		self.line.Draw()

################# LEBENSDAUER VON POSITRONEN IN FESTKÖRPERN ######################

def tkaToHist( filename , xMin = 0, xMax = 0 , giveTime = False):
	'''
	converts *TKA file to histogram
	input:
	filename: TKA file
	xMin: first bin, used to make a first cut
	xMax: last bin
	output:
	histogram containing data of TKA file
	'''

	from ROOT import TH1F

	# the first column contains the numbers, the second the \r
	# first two numbers are length and time and are ciscarded
	data = readFile( filename )[0]
	time = data[0] # or data[1]
	data = data[2:-1] #effective data

	length = len( data )

	if xMax == 0:
		xMax = length
	length = int( xMax - xMin )

	hist = TH1F('', ";Kanalnummer;Normierte Eintr#ddot{a}ge", length, xMin-0.5, xMax-0.5 )
	for i in range( length ):
		hist.SetBinContent(i, data[ i + xMin ] )

	hist.Sumw2()
	if giveTime:
		return hist, time
	else:
		return hist


def safeHist (hist, filename ):
	from ROOT import TFile
	outputfile = TFile( filename, "RECREATE")
	hist.Write()
	outputfile.Close()

def randomName():
	from random import randint
	from sys import maxint
	return str(randint(0,maxint))


