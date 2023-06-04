import requests
import json
import sqlite3
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

#TODO: Fix this garbage code style and merge two functions

def add_data_to_google_fit(type: int):
    data_source_id_steps = "derived:com.google.step_count.delta:380026818964:FitBridge:FitBridge:1:FitBridge" #TODO: Get from user
    data_source_id_heart_rate = "derived:com.google.heart_rate.bpm:380026818964:FitBridge:FitBridge:1:FitBridge" #TODO: Get from user

    if type == 0: #steps
        name = "Steps"
        data_source_id = data_source_id_steps
        latest_timestamp_file_name = "last_update_steps"
        column_name = "STEPS"
        query_condition = "STEPS > 0"
        dataTypeName = "com.google.step_count.delta"
        unit_type = "intVal"
        cast_command = int
    elif type == 1: #heart_rate
        name = "Heart Rate"
        data_source_id = data_source_id_heart_rate
        latest_timestamp_file_name = "last_update_heart_rate"
        column_name = "HEART_RATE"
        query_condition = "HEART_RATE > 0 AND HEART_RATE < 255"
        dataTypeName = "com.google.heart_rate.bpm"
        unit_type = "fpVal"
        cast_command = float
    else:
        return

    conn = sqlite3.connect("gbdata.sql") #TODO: Get from user
    cur = conn.cursor()
    if os.path.exists(latest_timestamp_file_name):
        with open(latest_timestamp_file_name, "r") as f:
            latest_timestamp = f.read()
        cur.execute(f"SELECT TIMESTAMP, {column_name} FROM MI_BAND_ACTIVITY_SAMPLE WHERE {query_condition} AND TIMESTAMP > {latest_timestamp} ORDER BY TIMESTAMP ASC")
    else:
        cur.execute(f"SELECT TIMESTAMP, {column_name} FROM MI_BAND_ACTIVITY_SAMPLE WHERE {query_condition} ORDER BY TIMESTAMP ASC")
    rows = cur.fetchall()
    conn.close()

    print(f"{name}: Read {len(rows)} Rows")
    if len(rows) == 0:
        return

    data_points = []

    for row in rows:
        timestamp = row[0]
        data = row[1]

        data_point = {
            "startTimeNanos": timestamp * 1000000000,
            "endTimeNanos": (timestamp + 10) * 1000000000,
            "dataTypeName": dataTypeName,
            "originDataSourceId": "",
            "value": [
                {
                    unit_type: cast_command(data)
                }
            ]
        }

        data_points.append(data_point)

    dataset = {
        "dataSourceId": data_source_id,
        "maxEndTimeNs": max(data_point["endTimeNanos"] for data_point in data_points), 
        "minStartTimeNs": min(data_point["startTimeNanos"] for data_point in data_points),
        "point": data_points
    }

    dataset_json = json.dumps(dataset)

    start_time = dataset["minStartTimeNs"]
    end_time = dataset["maxEndTimeNs"]

    request_url = base_url + "dataSources/" + data_source_id + "/datasets/" + str(start_time) + "-" + str(end_time)

    #print(dataset_json)

    response = session.patch(request_url, data=dataset_json)

    latest_timestamp = end_time // 1000000000

    if response.status_code == 200:
        print(f"{name}: The dataset was successfully inserted.")

        with open(latest_timestamp_file_name, "w+") as f:
            f.write(str(latest_timestamp))
    else:
        print(f"The dataset insertion failed: {response.status_code} {response.reason} {response.text}")


    print(f"{name}: The latest timestamp inserted is {latest_timestamp}")



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

add_data_to_google_fit(0)
add_data_to_google_fit(1)


