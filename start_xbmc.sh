#!/bin/sh

# synchronization of my laptop database and netbox database
#/home/martin/xbmc-scripts/update_macbook.sh

# check if xbmc is launched, if not, proceed to launch
pid=`pidof xbmc.bin`
echo $pid
if [ $pid ]
then
	echo "XBMC marche"
else
	DISPLAY=:0 xbmc &
fi

