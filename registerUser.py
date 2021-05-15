from flask import Flask,render_template,request
import json
import pickle
app = Flask(__name__)

@app.route("/")
def display_user_form():
    return render_template('form.html')

@app.route('/getStateDistrictMapper', methods = ['GET'])
def get_state_district_mapper():
    with open("helper/stateDistrictMapping.js", "rb") as f:
        jsonData = f.read()
    return jsonData 

@app.route('/addUser', methods = ['POST', 'GET'])
def add_user():
    if request.method == 'GET':
        return f"The URL /addUser is accessed directly. Try going to '/' to add an user"
    if request.method == 'POST':
        alertDetails = {}
        alertDetails["name"] = request.form.get("name")
        alertDetails["whatsapp"] = request.form.get("whatsapp")
        alertDetails["district_list"] = [int(distCode) for distCode in request.form.getlist("districts")]
        try:
        	alertDetails["pincodes"] = [int(pins) for pins in request.form.get("pinCodes").split("\r\n")]
        except ValueError:
        	pass
        alertDetails["senior_citizen"] = request.form.get("senior")
        userList = []
        try:
        	with open("data/Users.pickle", "rb") as f:
        		userList = pickle.load(f)
        		
        except FileNotFoundError:
        	pass

        with open("data/Users.pickle", "wb") as f:
        	userList.append(alertDetails)
        	pickle.dump(userList, f)

        return "User Registered Successfully"

if __name__ == '__main__':
    app.run(debug=True)