Various scripts to ease my use of XBMC.
=================

Here is a small explanations of all the scripts. I'll try to update them often, making them better and better !

Last update:
------------
Added this beautiful readme ;)

To do:
------------
add syslog support 

Description of the scripts:
---------------------------
**handle_xbmc_db.py** - Compares a sqlite database (moving computer) with a mysql database (server), adds bookmarks if necessary (to resume playing at the correct time) and updates playcount

**start_xbmc.sh** - Simple script to launch xbmc from wiimote ;)

**update_macbook.sh** - copies the remote sqlite database using ssh, calls the python script to handle changes and uploads the file back

**wminput_xbmc** - my configuration for wminput, to handle XBMC with a wiimote