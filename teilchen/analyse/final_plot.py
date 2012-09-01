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
from ROOT import TMultigraph

gROOT.Reset()

def waitForInput():
    raw_input("Press any key to continue!")
    return
 
final = TMultigraph()
    
canv = TCanvas( 'canv', 'final_plot', 200, 10, 700, 500 )
#~ canv.SetFillColor(0)
canv.cd()
nvalues = int(10.0)
x = array('d')
y = array('d')
ex = array('d')
ey= array('d')
for i in range(nvalues):
	x.append(i)
	ex.append(0.0)
	y.append (random.random()*10)
	ey.append(y[-1]*0.01)
fplot = TGraphErrors (nvalues,x,y,ex,ey)
fplot.Print()
Nbins = fplot.GetXaxis().GetNbins()
for bi in range(1,Nbins):
	fplot.GetXaxis().SetBinLabel(bi,"")
step = int(Nbins/7)
fplot.Draw("ap")
for i in (1,2):
	fplot.GetXaxis().SetBinLabel(step+Nbins/2*(i-1),"Z-Kompensation")
	fplot.GetXaxis().SetBinLabel(step*2+Nbins/2*(i-1),"Stabilitaet")
	fplot.GetXaxis().SetBinLabel(step*3+Nbins/2*(i-1),"Resonanz")
fplot.GetXaxis().LabelsOption("h")
fplot.SetTitle("Zusammenfassung der Ergebnisse")

textair = TPaveText(0.1,0.8,0.35,0.88,"NDC")
textair.AddText("Luft")
textair.SetFillColor(0)
textair.SetBorderSize(0)
textair.Draw("same")
textvac = TPaveText(0.55,0.8,0.88,0.88,"NDC")
textvac.SetFillColor(0)
textvac.SetBorderSize(0)
textvac.AddText("Vakuum")
textvac.Draw("same")


canv.Update()
canv.GetFrame().SetFillColor( 0 )
canv.GetFrame().SetBorderSize( 12 )
canv.Modified()
canv.Update()
canv.SaveAs("test.pdf")
