#!/bin/bash

# name of the video database on slave sqlite
videodb="MyVideos34.db"
dest="192.168.20.100"

LOG="/home/martin/log/xbmc-synchro"
SCRIPT_SOURCE="/home/martin/xbmc-scripts"

cd $SCRIPT_SOURCE


# test if the host is on the network
VAR=`ping -s 1 -c 1 $dest > /dev/null; echo $?`
if [ $VAR -eq 0 ] 
then
	# copy the db locally
	scp -P 22 martinea@macbook:"/Users/martin/Library/Application\ Support/XBMC/userdata/Database/$videodb" ./ 
	# handle changes
	./handle_xbmc_db.py >> $LOG 2>&1
	
	# copy the db back
	scp -P 22 ./$videodb martinea@macbook:"/Users/martin/Library/Application\ Support/XBMC/userdata/Database/"  
	
	rm $videodb
fi
