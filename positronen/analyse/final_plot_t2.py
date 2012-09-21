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

def Compare_val(val,err_val_stat,err_val_sys,val_theo,err_theo):
	#function returns how many standard deviations are between theory
	# and measurement
	from math import sqrt
	d = 1. * abs(val_theo - val)
	err_comb = sqrt(err_val_stat**2 + err_val_sys **2 + err_theo**2 )
	return d/err_comb


def waitForInput():
    raw_input("Press any key to continue!")
    return
def Fillx (ylist,xlist,exlist,xval):
	for i in range(len(ylist)):
		xlist.append(xval+0.5/len(ylist)*i)
		exlist.append(0.0)
	return

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

#~ ##############Tau 2####################
yzl2 = array('d')
yzl2.append(1.791)

eyzl2 = array('d')
eyzl2.append(0.097)

#global
ysl2 = array('d')
ysl2.append(1.968)

eysl2 = array('d')
eysl2.append(0.021)


##Aluminium###
#linear
yzv2 = array('d')
yzv2.append(1.965)

eyzv2 = array('d')
eyzv2.append(0.074)

#global
ysv2 = array('d')
ysv2.append(2.244)

eysv2 = array('d')
eysv2.append(0.079)

xzl2 = array('d')
exzl2 = array('d')
Fillx(yzl2,xzl2,exzl2,3.7)

xsl2 = array('d')
exsl2 = array('d')
Fillx(ysl2,xsl2,exsl2,7.9)

xzv2 = array('d')
exzv2 = array('d')
Fillx(yzv2,xzv2,exzv2,3.8)

xsv2 = array('d')
exsv2 = array('d')
Fillx(ysv2,xsv2,exsv2,8.0)

svGraph2 = TGraphErrors (len(ysv2),xsv2,ysv2,exsv2,eysv2)
svGraph2.SetMarkerStyle(34)
svGraph2.SetMarkerColor(2)
svGraph2.SetLineColor(2)
svGraph2.SetLineWidth(3)
svGraph2.SetMarkerSize(3.0)

zvGraph2 = TGraphErrors(len(yzv2),xzv2,yzv2,exzv2,eyzv2)
zvGraph2.SetMarkerStyle(23)
zvGraph2.SetMarkerColor(2)
zvGraph2.SetLineColor(2)
zvGraph2.SetLineWidth(3)
zvGraph2.SetMarkerSize(3.0)

slGraph2 = TGraphErrors (len(ysl2),xsl2,ysl2,exsl2,eysl2)
slGraph2.SetMarkerStyle(34)
slGraph2.SetMarkerColor(4)
slGraph2.SetLineColor(4)
slGraph2.SetLineWidth(3)
slGraph2.SetMarkerSize(3.0)

zlGraph2 = TGraphErrors (len(yzl2),xzl2,yzl2,exzl2,eyzl2)
zlGraph2.SetMarkerStyle(23)
zlGraph2.SetMarkerColor(4)
zlGraph2.SetLineColor(4)
zlGraph2.SetLineWidth(3)
zlGraph2.SetMarkerSize(3.0)

final.Add(svGraph2)
final.Add(zvGraph2)

final.Add(slGraph2)
final.Add(zlGraph2)
##### end Tau2    ######################

print "Polyethylen"
print "linear->global %.2fσ"%Compare_val(yzl2[0],eyzl2[0],0.,ysl2[0],eysl2[0])  
#~ print "linear->centroid %.2fσ"%Compare_val(yzl2[0],eyzl2[0],0.,yrl2[0],eyrl2[0]) 
#~ print "global->centroid %.2fσ"%Compare_val(ysl2[0],eys2[0],0,yrl2[0],eyrl2[0])) 
print ""
print "Aluminium"
print "linear->global %.2fσ"%Compare_val(yzv2[0],eyzv2[0],0.,ysv2[0],eysv2[0])  
#~ print "linear->centroid %.2fσ"%Compare_val(yzv[0],eyzv[0],0.,yrv[0],eyrv[0]) 
#~ print "global->centroid %.2fσ"%Compare_val(ysv[0],eys[0],0,yrv[0],eyrv[0])) 

######################

final.Draw("ap")
final.GetYaxis().SetTitle("#tau_{2} [ns]    ")
final.GetYaxis().RotateTitle(False)
final.GetXaxis().SetLimits(0.0,12.0)

final.SetMaximum(2.65)
#~ final.SetMinimum(5e-3)

#~ final.SetTitle("Zusammenfassung der Ergebnisse")

Nbins = final.GetXaxis().GetNbins()
for bi in range(1,Nbins):
	final.GetXaxis().SetBinLabel(bi,"")
step = int(Nbins/3)


i=1
final.GetXaxis().SetBinLabel(step-1+Nbins/2*(i-1),"Linearer Fit")
final.GetXaxis().SetBinLabel(step*2-2+7+Nbins/2*(i-1),'Globaler Fit')
#~ final.GetXaxis().SetBinLabel(step*3+15+Nbins/2*(i-1),"Centroid Shift")
	
	
final.GetXaxis().LabelsOption("h")
final.GetXaxis().SetLabelSize(0.06)
final.SetTitle("Zusammenfassung der Ergebnisse")

textair = TPaveText(0.35,0.75,0.5,0.88,"NDC")
textair.AddText("#tau_{2}")
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
leg.AddEntry(zlGraph2, "Polyethylen", "p")
leg.AddEntry(zvGraph2, "Aluminium", "p")
leg.Draw()

canv.Update()
canv.GetFrame().SetFillColor( 0 )
canv.GetFrame().SetBorderSize( 12 )
canv.Modified()
canv.Update()
canv.SaveAs("final_plot_2.pdf")
