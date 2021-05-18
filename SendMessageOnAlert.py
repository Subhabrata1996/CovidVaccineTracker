from twilio.rest import Client 
import time
import sys
import logging
import json
import pickle
import os

logging.basicConfig(level=logging.DEBUG, filename='logs/alerting.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def send_message(message, phoneNumber):
    messages = client.messages.create( 
                          from_='whatsapp:+14155238886',  
                          body=message,      
                          to='whatsapp:'+phoneNumber 
                      )
    print("Message Sent", messages.sid)
    time.sleep(2)

def pretty_format(center):
    return "\nDATE : \t" + str(center["date"]) + \
    "\nCENTER : \t" + str(center["center_id"]) + " - " + center["name"] + \
    "\nADDESSS : \t" + center["address"] + ", " + center["district_name"] + ", " + center["state_name"] + ", " + str(center["pincode"]) + \
    "\nVACCINE : \t" + center["vaccine"] + \
    "\nAVAILABLE : \t" + str(center["available_capacity_dose1"]) + \
    "\nMIN AGE LIMIT : \t" + str(center["min_age_limit"]) + "\n\n\n"        

account_sid = os.environ["ACCOUNT_SID"]
auth_token = os.environ["AUTH_TOKEN"]

client = Client(account_sid, auth_token) 


with open("helper/DistrictCodes.json", "rb") as f:
    DiscrictCodesMapper = json.load(f) 

while True:
    try:
        with open("data/Users.pickle", "rb") as f:
            usersList = pickle.load(f)   
    except FileNotFoundError:
        logging.debug("Users Not Found")
        time.sleep(60)
        continue

    try:
        with open("data/AvailableCenters.pickle", "rb") as f:
            availableCenters = pickle.load(f)
    except FileNotFoundError:
        logging.debug("Centers Not Found")
        time.sleep(60)
        continue

    sessions = {}
        
    try:
        with open("data/UserMessageSession.pickle", "rb") as f:
            sessions = pickle.load(f)   
    except FileNotFoundError:
        pass
    for user in usersList:
        if "district_list" in user:
            districtList = user["district_list"]
            districtNames = [DiscrictCodesMapper[str(distCode)] for distCode in districtList]
        else:
            districtNames = []
        if "pincodes" in user:    
            pincodeList = user["pincodes"]
        else:
            pincodeList = []    
        seniorCitizen = user["senior_citizen"] == "on"
        message = ""
        for center in availableCenters:
            if center["district_name"] in districtNames or center["pincode"] in pincodeList:
                if seniorCitizen or center["min_age_limit"] < 45 :
                    if user["whatsapp"] not in sessions:
                        sessions[user["whatsapp"]] = []
                    
                    if center["session_id"]+"_"+str(center["available_capacity_dose1"]) not in sessions[user["whatsapp"]]:
                        tempMessage = pretty_format(center)
                        if len(message + tempMessage) > 1600:
                            send_message(message, user["whatsapp"])
                            message = ""
                            time.sleep(2)
                        message = message+tempMessage
                        tempSession = sessions[user["whatsapp"]]
                        tempSession.append(center["session_id"] +"_"+str(center["available_capacity_dose1"]))
                        sessions[user["whatsapp"]] = tempSession
                        with open("data/UserMessageSession.pickle", "wb") as f:
                            pickle.dump(sessions, f)
        if len(message) != 0:
            send_message(message, user["whatsapp"])
            time.sleep(2)                

    time.sleep(2)                        

                     