#!/bin/bash
echo Starting the User Registration Application registerUser.py in background,
nohup python3 -u registerUser.py > logs/register.log &
echo Started Application - registerUser.py
echo ============================================================================================================
echo ============================================================================================================
echo Starting the User Whatsapp Message Sender Application SendMessageOnAlert.py in background,
echo Check logs/alerting.log for more details
nohup python3 -u SendMessageOnAlert.py > logs/alerting.log &
echo Started Application - SendMessageOnAlert.py

echo ============================================================================================================
echo ============================================================================================================
echo Starting the Vaccine Tracker Application track.py in background,
echo Check logs/tracker.log for more details
nohup python3 -u track.py > logs/tracker.log &
echo Started Application - track.py

echo ============================================================================================================
echo ============================================================================================================

echo Please note the process IDs of running python scripts below, use kill -9 PID to kill the application
ps -aux | grep python3 | grep 'track.py\|registerUser.py\|SendMessageOnAlert.py'

echo ============================================================================================================
