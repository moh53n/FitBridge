import requests
import json
import sqlite3
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import appdirs
import configparser
import shutil
import sys

#TODO: Fix this garbage code style and merge two functions

def add_data_to_google_fit(type: int, conf_dir, session, config):
    data_source_id_steps = config['CONFIG']["data_source_id_steps"]
    data_source_id_heart_rate = config['CONFIG']["data_source_id_heart_rate"]

    base_url = "https://www.googleapis.com/fitness/v1/users/me/"

    if type == 0: #steps
        name = "Steps"
        data_source_id = data_source_id_steps
        latest_timestamp_file_name = os.path.join(conf_dir, "last_update_steps")
        column_name = "STEPS"
        query_condition = "STEPS > 0"
        dataTypeName = "com.google.step_count.delta"
        unit_type = "intVal"
        cast_command = int
    elif type == 1: #heart_rate
        name = "Heart Rate"
        data_source_id = data_source_id_heart_rate
        latest_timestamp_file_name = os.path.join(conf_dir, "last_update_heart_rate")
        column_name = "HEART_RATE"
        query_condition = "HEART_RATE > 0 AND HEART_RATE < 255"
        dataTypeName = "com.google.heart_rate.bpm"
        unit_type = "fpVal"
        cast_command = float
    else:
        return

    conn = sqlite3.connect(config['CONFIG']["db_path"])
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

def auth(conf_dir):
    scope = ["https://www.googleapis.com/auth/fitness.activity.write", "https://www.googleapis.com/auth/fitness.activity.read",
             "https://www.googleapis.com/auth/fitness.heart_rate.read", "https://www.googleapis.com/auth/fitness.heart_rate.write"]

    credentials_file = os.path.join(conf_dir, "token.pickle")

    if os.path.exists(credentials_file):
        with open(credentials_file, "rb") as f:
            credentials = pickle.load(f)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(os.path.join(conf_dir, "client_secret.json"), scopes=scope)

        credentials = flow.run_console()

        with open(credentials_file, "wb") as f:
            pickle.dump(credentials, f)

    if not credentials.valid or credentials.expired:
        credentials.refresh(Request())

    return credentials

def register_datasources(credentials):
    heart_rate_reg_json = """{
    "dataStreamName": "FitBridge",
    "type": "derived",
    "application": {
      "detailsUrl": "https://github.com/moh53n/FitBridge",
      "name": "FitBridge",
      "version": "1"
    },
    "dataType": {
      "name": "com.google.heart_rate.bpm"
    },
    "device": {
      "manufacturer": "FitBridge",
      "model": "FitBridge",
      "type": "tablet",
      "uid": "1",
      "version": "1.0"
    }
  }"""
    
    steps_reg_json = """{
    "dataStreamName": "FitBridge",
    "type": "derived",
    "application": {
      "detailsUrl": "https://github.com/moh53n/FitBridge",
      "name": "FitBridge",
      "version": "1"
    },
    "dataType": {
      "field": [
        {
          "name": "steps",
          "format": "integer"
        }
      ],
      "name": "com.google.step_count.delta"
    },
    "device": {
      "manufacturer": "FitBridge",
      "model": "FitBridge",
      "type": "tablet",
      "uid": "1",
      "version": "1.0"
    }
  }
  """
    
    steps_reg_res = requests.post(url="https://www.googleapis.com/fitness/v1/users/me/dataSources", 
                  headers={"Authorization": "Bearer " + credentials.token}, 
                  data=steps_reg_json)
    if (steps_reg_res.status_code == 200 or steps_reg_res.status_code == 201):
        steps_ds_id = json.loads(steps_reg_res.text)['dataStreamId']
        print(f"The steps DataSource was successfully registered: {steps_ds_id}")
    elif (steps_reg_res.status_code == 409):
        steps_ds_id = json.loads(steps_reg_res.text)['error']['message'].split(' ')[2]
        print(f"The steps DataSource already existing: {steps_ds_id}")
    else:
        print(f"The steps DataSource registering failed: {steps_reg_res.status_code} {steps_reg_res.reason} {steps_reg_res.text}")
        return False

    heart_rate_reg_res = requests.post(url="https://www.googleapis.com/fitness/v1/users/me/dataSources", 
                  headers={"Authorization": "Bearer " + credentials.token}, 
                  data=heart_rate_reg_json)
    if (heart_rate_reg_res.status_code == 200 or heart_rate_reg_res.status_code == 201):
        heartrate_ds_id = json.loads(heart_rate_reg_res.text)['dataStreamId']
        print(f"The heart_rate DataSource was successfully registered: {heartrate_ds_id}")
    elif (heart_rate_reg_res.status_code == 409):
        heartrate_ds_id = json.loads(heart_rate_reg_res.text)['error']['message'].split(' ')[2]
        print(f"The heart_rate DataSource already existing: {heartrate_ds_id}")
    else:
        print(f"The heart_rate DataSource registering failed: {heart_rate_reg_res.status_code} {heart_rate_reg_res.reason} {heart_rate_reg_res.text}")
        return False
    
    return(steps_ds_id, heartrate_ds_id)

def setup_conf(conf_dir):
    if (input("\nIt seems that you are running this script for the first time (or the config directory is lost), Do you want to create a new config? (y/n): ").lower() != 'y'):
        return False
    json_path = input("\nEnter the path to the client_secret.json file: ")

    if not os.path.exists(json_path):
        print("\nThe provided file does not exist!")
        return False
    
    with open(json_path, "r") as f:
        json_obj = json.load(f)

    if "installed" not in json_obj.keys():
        print("\nThe provided file is malformed/incorrect!")
        return False
    
    if os.path.exists(os.path.join(conf_dir, "client_secret.json")):
        os.remove(os.path.join(conf_dir, "client_secret.json"))
    shutil.copy(json_path, os.path.join(conf_dir, "client_secret.json"))

    db_path = input("\nEnter the path to the Exported GadgetBridge database file: ")
    if not os.path.exists(db_path):
        print("\nThe provided file does not exist!")
        return False
    db_path = os.path.abspath(db_path)

    if (input("\nAdding DataSources to the API automatically? (If not, you have to create them manually and add data_source_ids to the config) (y/n): ").lower() == 'y'):
        credentials = auth(conf_dir)
        ds_res = register_datasources(credentials)
        if not ds_res:
            return False

    config = configparser.ConfigParser()
    config['CONFIG'] = {}
    config['CONFIG']["db_path"] = db_path
    config['CONFIG']["data_source_id_steps"] = ds_res[0]
    config['CONFIG']["data_source_id_heart_rate"] = ds_res[1]

    with open(os.path.join(conf_dir, "config.ini"), 'w+') as configfile:
        config.write(configfile)

    print("\nDone!")
    return True


def config_dir_check(conf_dir):
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir, exist_ok=True)

def config_check(conf_dir):
    if not os.path.exists(os.path.join(conf_dir, "config.ini")):
        if not setup_conf(conf_dir):
            print("Config setup failed...")
            return False
    
    config = configparser.ConfigParser()
    config.read(os.path.join(conf_dir, "config.ini"))
    if config['CONFIG']["db_path"] and config['CONFIG']["data_source_id_steps"] and config['CONFIG']["data_source_id_heart_rate"]:
        return config
    else:
        print("Config file is malformed!")
        return False

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\n\tFitBridge [ARGS]\n\n\t\t-h/--help  \tShow this message\n\t\t--get-token\tGet a Bearer token from Google API service and exit\n")
        return True

    conf_dir = appdirs.user_config_dir("FitBridge")

    config_dir_check(conf_dir)
    config = config_check(conf_dir)
    if not config:
        return False

    credentials = auth(conf_dir)

    if "--get-token" in sys.argv:
        print("\n" + credentials.token + "\n")
        return True

    session = requests.Session()
    session.headers.update({"Authorization": "Bearer " + credentials.token})



    add_data_to_google_fit(0, conf_dir, session, config)
    add_data_to_google_fit(1, conf_dir, session, config)


if __name__ == "__main__":
    main()
