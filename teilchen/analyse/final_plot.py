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
from ROOT import TGraphAsymmErrors

gROOT.Reset()

def waitForInput():
    raw_input("Press any key to continue!")
    return
def Fillx (ylist,xlist,exlist,xval):
	for i in range(len(ylist)):
		xlist.append(xval+0.5/len(ylist)*i)
		exlist.append(0.0)
	return

final = TMultiGraph()

canv = TCanvas( 'canv', 'final_plot', 200, 10, 700, 500 )
canv.SetLogy()
canv.SetBatch()
canv.SetGridy()
canv.cd()
nvalues = int(10.0)
ysl = array('d')
ysl.append(0.201)
ysl.append(0.04)

yzl = array('d')
yzl.append(5.95)
yzl.append(3.27)
yzl.append(1.09)

yrl = array('d')
yrl.append(0.3)
yrl.append(0.11)


ysv = array('d')
ysv.append(0.569)
ysv.append(0.637)
ysv.append(0.131)
ysv.append(0.509)


yzv = array('d')
yzv.append(4.4)

yrv = array('d')
yrv.append(0.17)
yrv.append(0.09)

eysl = array('d')
eysl.append(0.024  *3)
eysl.append(0.027  *3)


eyzl = array('d')
eyzl.append(1.75)
eyzl.append(2.23)
eyzl.append(0.23)

eyrl_high = array('d')
eyrl_high.append(0.1 )
eyrl_high.append(0.03 )

eyrl_low = array('d')
eyrl_low.append(999999)
eyrl_low.append(999999)

eysv = array('d')
eysv.append(0.088  *3)
eysv.append(0.087  *3)
eysv.append(0.040  *3)
eysv.append(0.047  *3)

eyzv = array('d')
eyzv.append(1.76)

eyrv_high = array('d')
eyrv_high.append(0.04 )
eyrv_high.append(0.09 )

eyrv_low = array('d')
eyrv_low.append(99999)
eyrv_low.append(99999)



xzl = array('d')
exzl = array('d')
Fillx(yzl,xzl,exzl,1.)

xsl = array('d')
exsl = array('d')
Fillx(ysl,xsl,exsl,2.9)

xrl = array('d')
exrl = array('d')
Fillx(yrl,xrl,exrl,4.9)


xzv = array('d')
exzv = array('d')
Fillx(yzv,xzv,exzv,6.8)

xsv = array('d')
exsv = array('d')
Fillx(ysv,xsv,exsv,8.9)

xrv = array('d')
exrv = array('d')
Fillx(yrv,xrv,exrv,10.8)

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

svGraph = TGraphErrors (len(ysv),xsv,ysv,exsv,eysv)
svGraph.SetMarkerStyle(34)
svGraph.SetMarkerColor(2)
svGraph.SetMarkerSize(1.0)


rvGraph = TGraphAsymmErrors (len(yrv),xrv,yrv,exrv,exrv,eyrv_low,eyrv_high)
rvGraph.SetMarkerStyle(29)
rvGraph.SetMarkerColor(34)
rvGraph.SetMarkerSize(1.0)

zvGraph = TGraphErrors (len(yzv),xzv,yzv,exzv,eyzv)
zvGraph.SetMarkerStyle(23)
zvGraph.SetMarkerColor(4)
zvGraph.SetMarkerSize(1.0)

slGraph = TGraphErrors (len(ysl),xsl,ysl,exsl,eysl)
slGraph.SetMarkerStyle(34)
slGraph.SetMarkerColor(2)
slGraph.SetMarkerSize(1.0)

rlGraph = TGraphAsymmErrors (len(yrl),xrl,yrl,exrl,exrl,eyrl_low,eyrl_high)
rlGraph.SetMarkerStyle(29)
rlGraph.SetMarkerColor(34)
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
final.GetYaxis().SetTitle("- #frac{q}{m} [#frac{mC}{kg}]")
final.GetYaxis().RotateTitle(False)
final.GetXaxis().SetLimits(0.0,12.0)

final.SetMaximum(10)
final.SetMinimum(5e-3)

final.SetTitle("Zusammenfassung der Ergebnisse")

Nbins = final.GetXaxis().GetNbins()
for bi in range(1,Nbins):
	final.GetXaxis().SetBinLabel(bi,"")
step = int(Nbins/8)


for i in (1,2):
	final.GetXaxis().SetBinLabel(step+-1+Nbins/2*(i-1),"Z-Kompensation")
	final.GetXaxis().SetBinLabel(step*2+4+Nbins/2*(i-1),'Stabilit#ddot{a}t')
	final.GetXaxis().SetBinLabel(step*3+6+Nbins/2*(i-1),"Resonanz")
final.GetXaxis().LabelsOption("h")
final.GetXaxis().SetLabelSize(0.045)
final.SetTitle("Zusammenfassung der Ergebnisse")

textair = TPaveText(0.2,0.8,0.35,0.88,"NDC")
textair.AddText("Luft")
textair.SetFillColor(0)
textair.SetBorderSize(0)
textair.Draw("same")
textvac = TPaveText(0.59,0.8,0.88,0.88,"NDC")
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
canv.SaveAs("final_plot.pdf")
