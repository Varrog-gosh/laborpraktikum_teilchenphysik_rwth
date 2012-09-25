#!/bin/bash
# This script calculates the change due to met and et shifts


echo "+++++++++++++++++++++++++++++++++++++++++"
echo "		compare M_T							"
echo "+++++++++++++++++++++++++++++++++++++++++"
echo "\n No shifts"
python analyse.py -q 1
echo""
echo "\n E_T up"
python analyse.py -q 1 --datafile "d0_new2met0.root/MessTree"
echo "\n E_T down"
python analyse.py -q 1 --datafile "d0_new-2met0.root/MessTree"
echo "\n MET up"
python analyse.py -q 1 --datafile "d0_new0met2.root/MessTree"
echo "\n MET down"
python analyse.py -q 1 --datafile "d0_new0met-2.root/MessTree"


echo "+++++++++++++++++++++++++++++++++++++++++"
echo "		compare E_T							"
echo "+++++++++++++++++++++++++++++++++++++++++"
echo "No shifts"
python analyse.py -p el_et -q 1
echo "\n E_T up"
python analyse.py -q 1 -p el_et --datafile "d0_new2met0.root/MessTree"
echo "\n E_T down"
python analyse.py -q 1 -p el_et --datafile "d0_new-2met0.root/MessTree"
echo "\n MET up"
python analyse.py -q 1 -p el_et --datafile "d0_new0met2.root/MessTree"
echo "\n MET down"
python analyse.py -q 1 -p el_et --datafile "d0_new0met-2.root/MessTree"


