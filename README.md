# FitBridge
--WIP--    
Simple script to sync Gadgetbridge exported data to Google Fit 

## Install and Usage

This project is not recommended for normal users because it's not user friendly at all. I strongly suggest to only use this script if you know what you're doing.   
    
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
9. Run the script:
```
$ FitBridge 

It seems that you are running this script for the first time (or the config directory is lost), Do you want to create a new config? (y/n): y

Enter the path to the client_secret.json file: PATH_TO_CLIENT_SECRET

Enter the path to the Exported GadgetBridge database file: PATH_TO_GB_DB

Adding DataSources to the API automatically? (If not, you have to create them manually and add data_source_ids to the config) (y/n): y
The steps DataSource successfully registered: XXX
The heart_rate DataSource successfully registered:: XXX

Done!
```