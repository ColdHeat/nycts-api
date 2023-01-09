# NYCTrainSign Reconstructed API

This repo contains a reverse engineered version of the API that once powered the NYCTrainSign. 

In addition to providing the sign data to show weather and train arrival times, the API also serves an exploit to any internet connected NYCTrainSign to allow users to control it without needing the original (now defunct) app.

## Sign Setup

### Backup MicroSD Card

While this process isn't risky all data that currently exists on the sign will be wiped. To begin you should make a backup of the Micro SD card that's on the Raspbery Pi inside the sign so that you can restore back to it if needed. 

You should follow online instructions to backup the MicroSD card for the Raspberry Pi. Here is one page that you can follow: https://pimylifeup.com/backup-raspberry-pi/. 

### Wifi Connection Instructions

1. Plug in the sign. Wait for it to start showing data. The data is stale so its fairly useless. 

2. Press the button in the back. This button may be inside of the sign's case. In that case you will need to open the back panel and then push the button. It would be optimal if you put the button through the hole in the panel and taped it somewhere so you can access it in the future. The button will reset the wifi settings and reboot the server. 

3. Wait for the sign to reboot. Wait for the sign to say "READY TO PAIR"

4. Once the sign says "READY TO PAIR", look for a wifi network named "NYCTrainSign". Connect to this network with your computer or phone. 

5. Once you're connected browse to http://192.168.44.1:88/.

6. Look for your wifi network, select it, and provide the password. Note that the sign only supports 2.4Ghz networks. 

7. Your phone/computer should disconnect and the network should disappear. Continue with the rest of the restoration instructions.

### Sign Exploit Instructions

1. Connect the sign to wifi following the instructions above. 

2. Once the sign starts to connect to the custom restored API, the sign will eventually reset all its settings to default. Wait for the sign to say "trainsignapi.com" or "PLEASE REBOOT". 

3. Unplug the sign and wait at least 10 seconds. 

4. Plug the sign back in.

5. The sign should load up and then restart.

6. The sign should eventually settle on the same data as before. Copy down or take a picture of the code that's shown with "trainsignapi.com". You should now be able to control the sign from the website (https://www.trainsignapi.com/claim) with the control code. 

# Exploit

## Overview

There exists an `os.system` call on the sign that runs on sign bootup. This system call directly uses the sign's ID as part of the command. 

Roughly the sign pulls configuration at boot so roughly the exploit can be summarized with:

1. The sign is turned on and it attempts to retrieve configuration. This will loop forever until the sign retrieves something.
2. The sign will eventually send a request for an image logo. This request will contain the sign ID and client ID. We store this data and create a exploit sign config. 
3. On the sign’s next config request we serve our exploit to the sign. 
4. We instruct the user to restart their sign and our exploit is run on restart
5. The exploit updates any code that’s needed to pair it with our new server

## Video

https://www.youtube.com/watch?v=AuuPpuothe8
