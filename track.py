import datetime
import requests
import time
import sys
import logging
import pickle

logging.basicConfig(level=logging.DEBUG, filename='logs/tracker.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

SESSION = requests.Session()

def scrape_vaccine_centers(district = None, pin = None, date = datetime.datetime.now().strftime("%d-%m-%Y")):
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public"
    querystring = {"date" : date}
    if district:
        URL = URL + "/calendarByDistrict"
        querystring["district_id"] = district
    elif pin:
        URL = URL + "/calendarByPin"
        querystring["pincode"] = pin
    else:
        logging.debug("district or pin is required")
        return None
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'}
    response = SESSION.get(URL, params = querystring, headers=headers)
    return response.json()["centers"]

def all_available_slots(centers):
    availableCenters = []
    for center in centers:
        for session in center["sessions"]:
            if session['available_capacity'] > 0: 
                tempParentCenter = dict(center)
                del tempParentCenter["sessions"]
                tempParentCenter["date"] = session["date"]
                tempParentCenter["available_capacity"] = session["available_capacity"]
                tempParentCenter["min_age_limit"] = session["min_age_limit"]
                tempParentCenter["vaccine"] = session["vaccine"]
                tempParentCenter["session_id"] = session["session_id"]

                availableCenters.append(tempParentCenter)
    return availableCenters

def check_available_slots(districtList = [], pinCodeList = [], numberOfWeeks = 4):
    allAvailableCenters = []
    if districtList:
        for district in districtList:
            date = datetime.datetime.now()
            for i in range(numberOfWeeks):
                centers = scrape_vaccine_centers(district = district, date = date.strftime("%d-%m-%Y"))
                if len(centers) < 1:
                    break;
                availableCenters = all_available_slots(centers)
                allAvailableCenters.extend(availableCenters)
                date = date + datetime.timedelta(days=7)
                time.sleep(2)  
    if pinCodeList:
        for pinCode in pinCodeList:
            date = datetime.datetime.now()
            for i in range(numberOfWeeks):
                centers = scrape_vaccine_centers(pin = pinCode, date = date.strftime("%d-%m-%Y"))
                availableCenters = all_available_slots(centers)
                if len(availableCenters) < 1:
                    break;
                allAvailableCenters.extend(availableCenters)
                date = date + datetime.timedelta(days=7)
                time.sleep(2)            
                
    return allAvailableCenters  

def update_available_centers(allAvailableCenters):
    lastUpdatedStatus = []
    try:
        with open("data/AvailableCenters.pickle", "rb") as f:
            lastUpdatedStatus = pickle.load(f)
    except FileNotFoundError:
        with open("data/AvailableCenters.pickle", "wb") as f:
            pickle.dump(allAvailableCenters, f)
            return        
    res = sorted(lastUpdatedStatus, key = lambda ele: sorted(ele.items())) == sorted(allAvailableCenters, key = lambda ele: sorted(ele.items()))
    if not res:
        logging.info("Changes in Slots")
        with open("data/AvailableCenters.pickle", "wb") as f:
            pickle.dump(allAvailableCenters, f) 

try:
    while True:
        usersList = []
        try:
            with open("data/Users.pickle", "rb") as f:
                usersList = pickle.load(f)
        except FileNotFoundError:
            logging.warning("No Users Loaded Yet.. continuing")
            time.sleep(10)
            continue
                  
        districtList = set()
        pinCodeList = set()
        if len(usersList) == 0:
              logging.warning("No Users .. continuing")
              time.sleep(10)
              continue
        for user in usersList:
            if "district_list" in user:
                districtList.update(user["district_list"])
            if "pincodes" in user:
                pinCodeList.update(user["pincodes"])    
        allAvailableCenters = check_available_slots(districtList = districtList, pinCodeList = pinCodeList)
        update_available_centers(allAvailableCenters)
        time.sleep(5)
                  
except KeyboardInterrupt: 
    logging.info("Interrupted : Stopped monitoring")
    sys.exit(0)