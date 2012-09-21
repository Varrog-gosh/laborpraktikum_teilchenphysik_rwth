#!/usr/bin/python
# coding=utf8

import ROOT
import tools
import random

from array import array
from ROOT import TGraphErrors
from ROOT import TCanvas
from ROOT import TPaveText
from ROOT import gROOT
from ROOT import TMultiGraph
from ROOT import TLine
from ROOT import TGraphAsymmErrors,TLegend

gROOT.Reset()

def waitForInput():
    raw_input("Press any key to continue!")
    return
def Fillx (ylist,xlist,exlist,xval):
	for i in range(len(ylist)):
		xlist.append(xval+0.5/len(ylist)*i)
		exlist.append(0.0)
	return

def Compare_val(val,err_val_stat,err_val_sys,val_theo,err_theo):
	#function returns how many standard deviations are between theory
	# and measurement
	from math import sqrt
	d = 1. * abs(val_theo - val)
	err_comb = sqrt(err_val_stat**2 + err_val_sys **2 + err_theo**2 )
	return d/err_comb

final = TMultiGraph()

canv = TCanvas( 'canv', 'final_plot', 200, 10, 700, 1000 )
#~ canv.SetLogy()
canv.SetBatch()
canv.SetGridy()
canv.cd()
nvalues = int(10.0)

'''
Werte:
yzl = linearer Fit Poly
ysl = Global Fit Poly
yrl = Centroid Shift Poly

yzv = linearer Fit Alu
ysv = Global Fit Alu
yrv = Centroid Shift Alu

'''

#################Tau 1 ###############################
##Polyethylen###
#linear
yzl = array('d')
yzl.append(0.5632)

eyzl = array('d')
eyzl.append(0.0048)

#global
ysl = array('d')
ysl.append(0.433)

eysl = array('d')
eysl.append(0.011)

#centroid
yrl = array('d')
yrl.append(0.4592)

eyrl = array('d')
eyrl.append(0.0057)

##Aluminium###
#linear
yzv = array('d')
yzv.append(0.6234)

eyzv = array('d')
eyzv.append(0.0096)

#global
ysv = array('d')
ysv.append(0.4903)

eysv = array('d')
eysv.append(0.0093)

#centroid
yrv = array('d')
yrv.append(0.5066)
eyrv = array('d')
eyrv.append(0.0089)

xzl = array('d')
exzl = array('d')
Fillx(yzl,xzl,exzl,2.2)

xsl = array('d')
exsl = array('d')
Fillx(ysl,xsl,exsl,4.9)

xrl = array('d')
exrl = array('d')
Fillx(yrl,xrl,exrl,8.9)


xzv = array('d')
exzv = array('d')
Fillx(yzv,xzv,exzv,2.3)

xsv = array('d')
exsv = array('d')
Fillx(ysv,xsv,exsv,5)

xrv = array('d')
exrv = array('d')
Fillx(yrv,xrv,exrv,9)


svGraph = TGraphErrors (len(ysv),xsv,ysv,exsv,eysv)
svGraph.SetMarkerStyle(34)
svGraph.SetMarkerColor(2)
svGraph.SetLineColor(2)
svGraph.SetLineWidth(3)
svGraph.SetMarkerSize(3.0)


rvGraph = TGraphErrors (len(yrv),xrv,yrv,exrv,eyrv)
rvGraph.SetMarkerStyle(29)
rvGraph.SetMarkerColor(2)
rvGraph.SetLineColor(2)
rvGraph.SetLineWidth(3)
rvGraph.SetMarkerSize(3.0)

zvGraph = TGraphErrors(len(yzv),xzv,yzv,exzv,eyzv)
zvGraph.SetMarkerStyle(23)
zvGraph.SetMarkerColor(2)
zvGraph.SetLineColor(2)
zvGraph.SetLineWidth(3)
zvGraph.SetMarkerSize(3.0)

slGraph = TGraphErrors (len(ysl),xsl,ysl,exsl,eysl)
slGraph.SetMarkerStyle(34)
slGraph.SetMarkerColor(4)
slGraph.SetLineColor(4)
slGraph.SetLineWidth(3)
slGraph.SetMarkerSize(3.0)

rlGraph = TGraphErrors (len(yrl),xrl,yrl,exrl,eyrl)
rlGraph.SetMarkerStyle(29)
rlGraph.SetMarkerColor(4)
rlGraph.SetLineColor(4)
rlGraph.SetLineWidth(3)
rlGraph.SetMarkerSize(3.0)

zlGraph = TGraphErrors (len(yzl),xzl,yzl,exzl,eyzl)
zlGraph.SetMarkerStyle(23)
zlGraph.SetMarkerColor(4)
zlGraph.SetLineColor(4)
zlGraph.SetLineWidth(3)
zlGraph.SetMarkerSize(3.0)

final.Add(svGraph)
final.Add(rvGraph)
final.Add(zvGraph)

final.Add(slGraph)
final.Add(rlGraph)
final.Add(zlGraph)

#############end Tau 1#################
print "Polyethylen"
print "linear->global %.2fσ"%Compare_val(yzl[0],eyzl[0],0.,ysl[0],eysl[0])  
print "linear->centroid %.2fσ"%Compare_val(yzl[0],eyzl[0],0.,yrl[0],eyrl[0]) 
print "global->centroid %.2fσ"%Compare_val(ysl[0],eysl[0],0,yrl[0],eyrl[0])
print ""
print "Aluminium"
print "linear->global %.2fσ"%Compare_val(yzv[0],eyzv[0],0.,ysv[0],eysv[0])  
print "linear->centroid %.2fσ"%Compare_val(yzv[0],eyzv[0],0.,yrv[0],eyrv[0]) 
print "global->centroid %.2fσ"%Compare_val(ysv[0],eysv[0],0,yrv[0],eyrv[0])
#################################

final.Draw("ap")
final.GetYaxis().SetTitle("#tau_{1} [ns]   ")
final.GetYaxis().RotateTitle(False)
final.GetXaxis().SetLimits(0.0,12.0)

final.SetMaximum(0.65)
#~ final.SetMinimum(5e-3)

final.SetTitle("Zusammenfassung der Ergebnisse")

Nbins = final.GetXaxis().GetNbins()
for bi in range(1,Nbins):
	final.GetXaxis().SetBinLabel(bi,"")
step = int(Nbins/5)


i=1
final.GetXaxis().SetBinLabel(step-1+Nbins/2*(i-1),"Linearer Fit")
final.GetXaxis().SetBinLabel(step*2-2+7+Nbins/2*(i-1),'Globaler Fit')
final.GetXaxis().SetBinLabel(step*3+15+Nbins/2*(i-1),"Centroid Shift")
#~ i=2	
#~ final.GetXaxis().SetBinLabel(step+1+Nbins/2*(i-1),"Linearer Fit")
#~ final.GetXaxis().SetBinLabel(step*3-3+Nbins/2*(i-1),'Globaler Fit')	
	
final.GetXaxis().LabelsOption("h")
final.GetXaxis().SetLabelSize(0.06)
final.SetTitle("Zusammenfassung der Ergebnisse")

textair = TPaveText(0.35,0.75,0.5,0.88,"NDC")
textair.AddText("#tau_{1}")
textair.SetFillColor(0)
textair.SetBorderSize(0)
textair.Draw("same")
#~ textvac = TPaveText(0.47,0.8,0.77,0.88,"NDC")
#~ textvac.SetFillColor(0)
#~ textvac.SetBorderSize(0)
#~ textvac.AddText("#tau_{2}")
#~ textvac.Draw("same")

#~ line = TLine()
#~ line.SetLineWidth(2)
#~ line.SetLineStyle(9)
#~ line.DrawLineNDC(0.5,0.11,0.5,0.88)

leg = TLegend(0.6, 0.7, .95,.95)
leg.SetFillColor(0)
leg.SetLineWidth(0)
leg.AddEntry(zlGraph, "Polyethylen", "p")
leg.AddEntry(zvGraph, "Aluminium", "p")
leg.Draw()

canv.Update()
canv.GetFrame().SetFillColor( 0 )
canv.GetFrame().SetBorderSize( 12 )
canv.Modified()
canv.Update()
canv.SaveAs("final_plot_1.pdf")
