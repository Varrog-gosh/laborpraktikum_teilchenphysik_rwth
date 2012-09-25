#!/usr/bin/python
# coding=utf8


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


import ROOT

x = readFile('ergebnisse')
f = ROOT.TGraphErrors()

#q_0 = 1./12 / 128 * 80.38 / 0.23122
s_theo = 2.58
s_scaling = s_theo / 2.03540169874
s_mess = 2.63
s_mess_error = 0.39

for i in range(len(x[0])):

	nc = x[0][i]
	s_tot = x[1][i]
	#f.SetPoint(i, 1./x[0][i], x[1][i] )
	#f.SetPointError(i, 0, x[2][i] )
	s_scaled = s_tot/(2*nc+3)*s_scaling
	abw = abs(s_scaled - s_mess ) / s_mess_error
	print("{} & {:.2f} & {:.2f} & {:.2f} & {:.1f} \\\\".format(nc, s_tot, s_tot /(2*nc + 3), s_scaled, abw) )


#f.Draw("a*")
