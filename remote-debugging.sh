#!/bin/bash 
#DISPLAY=:7 sudo google-chrome-stable --remote-debugging-port=9222 --ignore-certificate-errors --user-data-dir=$TMPDIR/chrome-profiling --no-default-browser-check
sudo google-chrome-stable --remote-debugging-port=9222 --enable-benchmarking --enable-net-benchmarking --start-maximized  --ignore-certificate-errors --user-data-dir=$TMPDIR/chrome-profiling --no-default-browser-check
#sudo google-chrome-stable --proxy-port=8080 --remote-debugging-port=9222  --ignore-certificate-errors --user-data-dir=$TMPDIR/chrome-profiling --no-default-browser-check
