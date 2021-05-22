import json
import requests
import time
from datetime import date

from_email = <from_email> #Replace these variables
to_email = [<to_emails_separated_by_comma>]
api_key = "<api_key>"

num_times_executed = 0

def send_simple_message(text):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxaf972e30c0a74fa7bf7771702ccefc58.mailgun.org/messages",
		auth=("api", api_key),
		data={"from": from_email,
			"to": to_email,
			"subject": "Vaccine availability Notice",
			"html": text})


def notifier(prev_centers):
    today = date.today()
    todays_date = today.strftime("%d-%m-%Y")
    string_to_email = ""
    #############################################
    district_id = [294,265]  # SELECT THE DISTRICT IDS THAT ARE REQUIRED BY YOU
                                 # OPEN THIS IN A BROWSER TO GET YOUR STATE ID https://cdn-api.co-vin.in/api/v2/admin/location/states
                                 # OPEN THIS IN A BROWSER USING THE STATE ID ABOVE TO GET THE DISTRICT IT
                                 # https://cdn-api.co-vin.in/api/v2/admin/location/districts/<STATE_ID>
    ############################################
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    current_centers = []
    for dist in district_id:
        x = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id="+str(dist)+"&date="+todays_date,headers=header)
        data = json.loads(x.text)
        for center in data["centers"]:
            flag=0
            min_age=100
            slotsavail = []
            for session in center["sessions"]:
                if session["available_capacity"] != 0 and session["min_age_limit"]==18:
                    flag = 1
                    slotsavail.append(session["available_capacity"])
                    date_session = session["date"]
                    string_to_email += str(date_session)
                    if session["min_age_limit"] < min_age:
                        min_age=session["min_age_limit"]
            if flag == 1:
                current_centers.append(center["center_id"])
                string_to_email = string_to_email + "<br>" + str(center["name"])+"<br>"+ str(center["center_id"])+"<br>"+str(center["pincode"])+"<br>"+center["block_name"]+"<br>fee type:"+center["fee_type"]+"<br>min age:"+str(min_age)+"<br>avail slots"+str(slotsavail)+"<br>-----------------<br>"
    string_to_email = str(string_to_email)
    if string_to_email != "":
        string_to_email = "<strong>" + string_to_email + "</strong>"
        print("-------------------------\n",current_centers,"\n-------------------------\n")
        print("-------------------------\n",prev_centers,"\n-------------------------\n")
        if current_centers != prev_centers:
            new_centers = set(current_centers) - set(prev_centers)
            string_to_email = "New centers Added since last email <br>" + str(new_centers) + "<br>" + string_to_email
            print("Sending email...")
            response = send_simple_message(string_to_email)
            print(response.content)
        else:
            print("email skipped")
        return current_centers
    else:
        print("empty")
        return "empty"


prev_centers=[]
for x in range(100):
    prev_centers = notifier(prev_centers)
    num_times_executed+=1
    print("Number of times executed",num_times_executed)
    time.sleep(100) #Set time as required
