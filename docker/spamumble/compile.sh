#!/bin/bash

#######################
# Compile Murmur.ice
#
# Place Murmur.ice to this folder or let it download automatically
# and run this script
# the output files will be automatically copied to the destination
#
# Source: wget https://raw.githubusercontent.com/mumble-voip/mumble/master/src/murmur/Murmur.ice
#
# Ashley
######################

cd /opt/

if [ ! -f "Murmur.ice" ]; then
	echo "Murmur.ice file not found! Trying download"
	wget https://raw.githubusercontent.com/mumble-voip/mumble/master/src/murmur/Murmur.ice 2>/dev/null
	if [ ! -f "Murmur.ice" ]; then
		echo "Failed getting new Murmur.ice file. Cancelling!";
		exit 1
	fi
fi

rm Murmur_ice.py spamumble/Murmur_ice.py 2>/dev/null
rm Murmur/__init__.py spamumble/Murmur/__init.py 2>/dev/null
rm Murmur/__init__.pyc spamumble/Murmur/__init__.pyc 2>/dev/null

slice2py Murmur.ice -I/usr/share/Ice-3.5.1/slice

if [ ! -f "Murmur_ice.py" ]; then
	echo "Compilation failed!"
	exit 2
fi

mkdir spamumble/Murmur 2>/dev/null

mv Murmur_ice.py spamumble/Murmur_ice.py
mv Murmur/__init__.py spamumble/Murmur/__init__.py

rm Murmur.ice
rm -rf Murmur

echo "Done. Thanks for choosing our train and see you next time!"
