#!/bin/bash
# This script produces the graphics needed in lab report

./2dMtEt.py
./tauBackgroundEstimation.py -p mwt --save
./tauBackgroundEstimation.py -p met --cutline 30 --save
./tauBackgroundEstimation.py -p el_et -c 'met>30' --cutline 25 --save
./tauBackgroundEstimation.py -p mwt -c 'met>30&&el_et>25' --save
./analyse.py --save
./tauBackgroundEstimation.py -p "mwt/el_et" --cutline 1.7 --save

