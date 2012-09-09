''' for stability, calculate ordinate of fit values'''

from uncertainties import ufloat
import numpy
y = ["-113.161522564  +/- 24.1559875092",
"26.3560023073  +/- 50.4099140061",
"-69.3503185589  +/- 56.7122509259",
"-115.105245988  +/- 56.0641568581",
"-22.1584551362  +/- 32.2763627437",
"-50.4901873138  +/- 18.9218106161"]
means = []
weights = []

for i in y:
	means.append( ufloat(i).nominal_value)
	weights.append( ufloat(i).std_dev()**2)

val, error = numpy.average( numpy.array( means ) , weights = numpy.array( weights ) ,returned = True)

error = 1. / numpy.sqrt( error )
from tools import printError
printError( val, error)



