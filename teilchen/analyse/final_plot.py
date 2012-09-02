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

gROOT.Reset()

def waitForInput():
    raw_input("Press any key to continue!")
    return
def Fillx (ylist,xlist,exlist,xval):
	for i in range(len(ylist)):
		xlist.append(xval+1/len(ylist)*i)
		exlist.append(0.0)
	return
	
		 
final = TMultiGraph()
    
canv = TCanvas( 'canv', 'final_plot', 200, 10, 700, 500 )
canv.SetLogy()
canv.cd()
nvalues = int(10.0)
ysl = array('d')
ysl.append(100)
ysl.append(1000)

yzl = array('d')
yzl.append(100)
yzl.append(1200)

yrl = array('d')
yrl.append(123)
yrl.append(1223)

ysv = array('d')
ysv.append(21293)
ysv.append(2123)

yzv = array('d')
yzv.append(5239)
yzv.append(523)

yrv = array('d')
yrv.append(4320)
yrv.append(420)

eysl = array('d')
eysl.append(0.15*100)
eysl.append(0.15*1000)

eyzl = array('d')
eyzl.append(0.15*100)
eyzl.append(0.15*1200)

eyrl = array('d')
eyrl.append(0.15*123)
eyrl.append(0.15*1223)

eysv = array('d')
eysv.append(0.15*21293)
eysv.append(0.15*2123)

eyzv = array('d')
eyzv.append(0.15*5239)
eyzv.append(0.15*523)

eyrv = array('d')
eyrv.append(0.15*4320)
eyrv.append(0.15*420)

xsl = array('d')
exsl = array('d')
Fillx(ysl,xsl,exsl,4)

xzl = array('d')
exzl = array('d')
Fillx(yzl,xzl,exzl,5)

xrl = array('d')
exrl = array('d')
Fillx(yrl,xrl,exrl,6.5)


xsv = array('d')
exsv = array('d')
Fillx(ysv,xsv,exsv,8)

xzv = array('d')
exzv = array('d')
Fillx(yzv,xzv,exzv,9.1)
xrv = array('d')
exrv = array('d')
Fillx(yrv,xrv,exrv,10.3)

x = array("d")
y = array('d')
ex = array('d')
ey= array('d')
for i in range(nvalues):
	x.append(i)
	ex.append(0.0)
	y.append (random.random()*10)
	ey.append(y[-1]*0.01)
fplot = TGraphErrors (nvalues,x,y,ex,ey)

svGraph = TGraphErrors (2,xsv,ysv,exsv,eysv)
svGraph.SetMarkerStyle(23)
svGraph.SetMarkerColor(2)
svGraph.SetMarkerSize(1.0)


rvGraph = TGraphErrors (len(yrv),xrv,yrv,exrv,eyrv)
rvGraph.SetMarkerStyle(23)
rvGraph.SetMarkerColor(3)
rvGraph.SetMarkerSize(1.0)

zvGraph = TGraphErrors (len(yzv),xzv,yzv,exzv,eyzv)
zvGraph.SetMarkerStyle(23)
zvGraph.SetMarkerColor(4)
zvGraph.SetMarkerSize(1.0)

slGraph = TGraphErrors (len(ysl),xsl,ysl,exsl,eysl)
slGraph.SetMarkerStyle(23)
slGraph.SetMarkerColor(2)
slGraph.SetMarkerSize(1.0)

rlGraph = TGraphErrors (len(yrl),xrl,yrl,exrl,eyrl)
rlGraph.SetMarkerStyle(23)
rlGraph.SetMarkerColor(3)
rlGraph.SetMarkerSize(1.0)

zlGraph = TGraphErrors (len(yzl),xzl,yzl,exzl,eyzl)
zlGraph.SetMarkerStyle(23)
zlGraph.SetMarkerColor(4)
zlGraph.SetMarkerSize(1.0)

final.Add(svGraph)
final.Add(rvGraph)
final.Add(zvGraph)

final.Add(slGraph)
final.Add(rlGraph)
final.Add(zlGraph)

final.Draw("ap")
svGraph.SetTitle("Zusammenfassung der Ergebnisse")
Nbins = final.GetXaxis().GetNbins()
for bi in range(1,Nbins):
	final.GetXaxis().SetBinLabel(bi,"")
step = int(Nbins/7)


for i in (1,2):
	final.GetXaxis().SetBinLabel(step+Nbins/2*(i-1),"Z-Kompensation")
	final.GetXaxis().SetBinLabel(step*2+Nbins/2*(i-1),"Stabilitaet")
	final.GetXaxis().SetBinLabel(step*3+Nbins/2*(i-1),"Resonanz")
final.GetXaxis().LabelsOption("h")
final.GetXaxis().SetMinimum(0.0)
final.SetTitle("Zusammenfassung der Ergebnisse")

textair = TPaveText(0.2,0.8,0.35,0.88,"NDC")
textair.AddText("Luft")
textair.SetFillColor(0)
textair.SetBorderSize(0)
textair.Draw("same")
textvac = TPaveText(0.55,0.8,0.88,0.88,"NDC")
textvac.SetFillColor(0)
textvac.SetBorderSize(0)
textvac.AddText("Vakuum")
textvac.Draw("same")

line = TLine()
line.SetLineWidth(2)
line.SetLineStyle(9)
line.DrawLineNDC(0.5,0.11,0.5,0.88)

canv.Update()
canv.GetFrame().SetFillColor( 0 )
canv.GetFrame().SetBorderSize( 12 )
canv.Modified()
canv.Update()
canv.SaveAs("test.pdf")
