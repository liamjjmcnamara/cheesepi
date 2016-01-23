#Wifi Dongle problem Solution
#================================================
#================================================  
#Go to /etc/ifplugd/action.d/

#Rename the the ifupdown to ifupdown.original
mv ifupdown ifupdown.original

#Then copy /etc/wpa_supplicant/ifupdown.sh in to ./ifupdown

cp /etc/wpa_supplicant/ifupdown.sh ./ifupdown
