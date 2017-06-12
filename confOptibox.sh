#!/bin/bash
if [ -e /media/pi/OPTIBOX ]
then
	echo 'USB plugged' >> /home/pi/python/usbconf.log
	cd /media/pi/OPTIBOX
	if [ -e config.ini ]
	then
		mv -f config.ini /home/pi/python/conf
		echo 'done'  >> /home/pi/python/usbconf.log
		reboot
	else
		echo 'wrong USB' >> /home/pi/python/usbconf.log
	fi
elif [ -e /dev/sda1 ]
then
	echo 'USB plugged'  >> /home/pi/python/usbconf.log 
	mount /dev/sda1 /mnt/key
	cd /mnt/key
	if [ -e config.ini ]
	then
		mv -f config.ini /home/pi/python/conf
		echo 'done' >> /home/pi/python/usbconf.log 
		reboot
	else
		echo 'wrong USB' >> /home/pi/python/usbconf.log 
	fi
elif [ -e /dev/sdb1 ]
then
	echo 'USB plugged'  >> /home/pi/python/usbconf.log 
	mount /dev/sdb1 /mnt/key
	cd /mnt/key
	if [ -e config.ini ]
	then
		mv -f config.ini /home/pi/python/conf
		echo 'done' >> /home/pi/python/usbconf.log
		reboot
	else
		echo 'wrong USB' >> /home/pi/python/usbconf.log
	fi
	
else
	echo 'No USB found' >> /home/pi/python/usbconf.log
fi
