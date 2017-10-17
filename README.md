PLTSpeed
=======================

PLTSpeed uses [WProfX] and [WPR-GO] to build a controlled envirnment for Web performance analyses.

Content variations are controlled using [WPR-GO] and network variations are controlled using a combination of Linux network [namespace] and [TC].

[WProfX]: https://github.com/jnejati/WProfX
[WPR-GO]:https://github.com/catapult-project/catapult/blob/master/web_page_replay_go/README.md
[namespace]:http://man7.org/linux/man-pages/man7/namespaces.7.html
[TC]:http://tldp.org/HOWTO/Traffic-Control-HOWTO/intro.html

Setup
-----

### Directory Structure
The following directory structure is assumed:

    ParentDir/
    --PLTSpeed/
    --catapult/
      
### Installation
#### Catapult
1. Install __Go__ and follow the __catapult__ installation instructions
2. Run __wpr.patch__ on the __wpr.go__ file in _catapult/web_page_replay_go/src/_

#### Python Modules

    sudo pip3 install pyOpenSSL
    sudo pip3 install tldextract
    sudo pip3 install dnslib
    sudo pip3 install ripe
    sudo pip3 install ripe.atlas.sagan
    sudo pip3 install ripe.atlas.cousteau
  
#### Node.Js Modules

    npm install chrome-remote-interface@v0.23.3
    
Note: ```nodejs``` must be in your $PATH

### Data
The following data files are required:

    PLTSpeed/
    --ripe/
    ----ping_data
    ----dns_data
    
Runtime
-----

#### Chrome

Run chrome with remote debugging port 9222

    google-chrome-stable --remote-debugging-port=9222

#### Main Program

    [sudo -E] python3 main.py

Note1: This program will modify your _/etc/resolv.conf_ file. Please make sure you have a backup.

Note2: _sudo -E_ may be necessary to run properly
