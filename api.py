import requests
import json
import sqlite3
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

#TODO: Fix this garbage code style and merge two functions

def add_steps():
    data_source_id_steps = "derived:com.google.step_count.delta:380026818964:FitBridge:FitBridge:1:FitBridge" #TODO: Get from user

    conn = sqlite3.connect("gbdata.sql") #TODO: Get from user
    cur = conn.cursor()
    if os.path.exists("last_update_steps"):
        with open("last_update_steps", "r") as f:
            steps_latest_timestamp = f.read()

        cur.execute(f"SELECT TIMESTAMP, STEPS FROM MI_BAND_ACTIVITY_SAMPLE WHERE STEPS > 0 AND TIMESTAMP > {steps_latest_timestamp} ORDER BY TIMESTAMP ASC")
    else:
        cur.execute("SELECT TIMESTAMP, STEPS FROM MI_BAND_ACTIVITY_SAMPLE WHERE STEPS > 0 ORDER BY TIMESTAMP ASC")
    rows = cur.fetchall()
    conn.close()

    print(f"Steps: Read {len(rows)} Rows")
    if len(rows) == 0:
        return

    data_points = []

    for row in rows:
        timestamp = row[0]
        steps = row[1]

        data_point = {
            "startTimeNanos": timestamp * 1000000000,
            "endTimeNanos": (timestamp + 10) * 1000000000,
            "dataTypeName": "com.google.step_count.delta",
            "originDataSourceId": "",
            "value": [
                {
                    "intVal": steps
                }
            ]
        }

        data_points.append(data_point)

    dataset = {
        "dataSourceId": data_source_id_steps,
        "maxEndTimeNs": max(data_point["endTimeNanos"] for data_point in data_points), 
        "minStartTimeNs": min(data_point["startTimeNanos"] for data_point in data_points),
        "point": data_points
    }

    dataset_json = json.dumps(dataset)

    start_time = dataset["minStartTimeNs"]
    end_time = dataset["maxEndTimeNs"]

    request_url = base_url + "dataSources/" + data_source_id_steps + "/datasets/" + str(start_time) + "-" + str(end_time)

    #print(dataset_json)

    response = session.patch(request_url, data=dataset_json)

    steps_latest_timestamp = end_time // 1000000000 # convert nanoseconds to milliseconds

    if response.status_code == 200:
        print("The dataset was successfully inserted.")

        with open("last_update_steps", "w+") as f:
            f.write(str(steps_latest_timestamp))
    else:
        print(f"The dataset insertion failed: {response.status_code} {response.reason} {response.text}")


    print(f"The latest steps timestamp inserted is {steps_latest_timestamp}")




def add_heart_rate():
    data_source_id_heart_rate = "derived:com.google.heart_rate.bpm:380026818964:FitBridge:FitBridge:1:FitBridge" #TODO: Get from user

    conn = sqlite3.connect("gbdata.sql") #TODO: Get from user
    cur = conn.cursor()
    if os.path.exists("last_update_heart_rate"):
        with open("last_update_heart_rate", "r") as f:
            heart_rate_latest_timestamp = f.read()
        cur.execute(f"SELECT TIMESTAMP, HEART_RATE FROM MI_BAND_ACTIVITY_SAMPLE WHERE HEART_RATE > 0 AND HEART_RATE < 255 AND TIMESTAMP > {heart_rate_latest_timestamp} ORDER BY TIMESTAMP ASC")
    else:
        cur.execute("SELECT TIMESTAMP, HEART_RATE FROM MI_BAND_ACTIVITY_SAMPLE WHERE HEART_RATE > 0 AND HEART_RATE < 255 ORDER BY TIMESTAMP ASC")
    rows = cur.fetchall()
    conn.close()

    print(f"Heart Rate: Read {len(rows)} Rows")
    if len(rows) == 0:
        return

    data_points = []

    for row in rows:
        timestamp = row[0]
        heart_rate = row[1]

        data_point = {
            "startTimeNanos": timestamp * 1000000000,
            "endTimeNanos": (timestamp + 10) * 1000000000,
            "dataTypeName": "com.google.heart_rate.bpm",
            "originDataSourceId": "",
            "value": [
                {
                    "fpVal": float(heart_rate)
                }
            ]
        }

        data_points.append(data_point)

    dataset = {
        "dataSourceId": data_source_id_heart_rate,
        "maxEndTimeNs": max(data_point["endTimeNanos"] for data_point in data_points), 
        "minStartTimeNs": min(data_point["startTimeNanos"] for data_point in data_points),
        "point": data_points
    }

    dataset_json = json.dumps(dataset)

    start_time = dataset["minStartTimeNs"]
    end_time = dataset["maxEndTimeNs"]

    request_url = base_url + "dataSources/" + data_source_id_heart_rate + "/datasets/" + str(start_time) + "-" + str(end_time)

    #print(dataset_json)

    response = session.patch(request_url, data=dataset_json)

    heart_rate_latest_timestamp = end_time // 1000000000

    if response.status_code == 200:
        print("The dataset was successfully inserted.")

        with open("last_update_heart_rate", "w+") as f:
            f.write(str(heart_rate_latest_timestamp))
    else:
        print(f"The dataset insertion failed: {response.status_code} {response.reason} {response.text}")


    print(f"The latest timestamp inserted is {heart_rate_latest_timestamp}")





scope = ["https://www.googleapis.com/auth/fitness.activity.write", "https://www.googleapis.com/auth/fitness.activity.read",
         "https://www.googleapis.com/auth/fitness.heart_rate.read", "https://www.googleapis.com/auth/fitness.heart_rate.write"]

credentials_file = "token.pickle"

if os.path.exists(credentials_file):
    with open(credentials_file, "rb") as f:
        credentials = pickle.load(f)
else:
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scope)

    credentials = flow.run_console()

    with open(credentials_file, "wb") as f:
        pickle.dump(credentials, f)

if not credentials.valid or credentials.expired:
    credentials.refresh(Request())

session = requests.Session()
session.headers.update({"Authorization": "Bearer " + credentials.token})

#print(credentials.token)

base_url = "https://www.googleapis.com/fitness/v1/users/me/"

add_steps()
add_heart_rate()


