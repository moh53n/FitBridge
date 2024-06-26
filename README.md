# FitBridge
[![PyPI](https://img.shields.io/pypi/v/FitBridge)](https://pypi.org/project/FitBridge/)
[![Downloads](https://static.pepy.tech/badge/fitbridge)](https://pepy.tech/project/fitbridge)
![GitHub](https://img.shields.io/github/license/moh53n/FitBridge?color=black)    
**NOTE from Google: The Google Fit APIs, including the Google Fit REST API, will no longer be available after June 30, 2025. As of May 1, 2024, developers cannot sign up to use these APIs.**     
--    
A simple script to sync Gadgetbridge exported data to Google Fit. Currently, only the Mi Band data is supported.

## Install and Usage

This project is not recommended for normal users because it's not user friendly at all. I strongly suggest to only use this script if you know what you're doing.   
    
**You can install and run this script in Termux.**    
    
1. Go to the [Google API Console](https://console.cloud.google.com/flows/enableapi?apiid=fitness).    
2. Select a project, or create a new one.    
3. Click Continue to enable the Fitness API.    
4. Click Go to credentials.    
5. Click New credentials, then select OAuth Client ID (You may need to create a "OAuth consent screen" first, make sure you add your Google Fit account's Gmail address in "Test users" when creating a "OAuth consent screen").    
6. Under Application type, select "Desktop app".    
7. When the OAuth client is created, Click on "DOWNLOAD JSON".
8. Install FitBridge:    
```
pip install FitBridge
```    
9. Run the script for the initial setup:
```
$ FitBridge 

It seems that you are running this script for the first time (or the config directory is lost), Do you want to create a new config? (y/n): y

Enter the path to the client_secret.json file: PATH_TO_CLIENT_SECRET

Enter the path to the Exported GadgetBridge database file: PATH_TO_GB_DB

Adding DataSources to the API automatically? (If not, you have to create them manually and add data_source_ids to the config) (y/n): y
steps DataSource registered successfully: XXX
heart_rate DataSource registered successfully: XXX

Done!
```
10. After the initial setup is done, You can sync the new data from the Gadgetbridge exported database by simply running the script again (Only the unsynced data will be synced):
```
$ FitBridge
Steps: Read 10 Rows
Steps: dataset inserted successfully.
Steps: latest inserted timestamp is 2023-06-04 18:34:20 (UTC)
Heart Rate: Read 96 Rows
Heart Rate: dataset inserted successfully.
Heart Rate: latest inserted timestamp is 2023-06-04 18:34:20 (UTC)
```
