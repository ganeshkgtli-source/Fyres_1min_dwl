import pandas as pd
import sys
import time
import math
from datetime import datetime
import requests
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws  
from tkinter import messagebox
import webbrowser
 
from tkinter import simpledialog
import os
from datetime import date
from urllib.parse import urlparse, parse_qs
import json
import numpy as np
from rich import print
 
def get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type):
                session = fyersModel.SessionModel(
                    client_id=client_id,
                    secret_key=secret_key,
                    redirect_uri=redirect_uri,
                    response_type=response_type
                )
                response = session.generate_authcode()
                ##print(response)
                chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                url = response  # Replace with the URL you want to open
 
                data=webbrowser.get(chrome_path).open(url)
                time.sleep(0.10)
                ##print(data)
                enter_uri = simpledialog.askstring("Enter URL", "Enter the URL:")
                parsed_url = urlparse(enter_uri)
                if enter_uri:
                    query_parameters = parse_qs(parsed_url.query)
 
                    auth_code = query_parameters.get('auth_code')
 
                    if auth_code:
                        auth_code_value = auth_code[0]
                        #print(f"Extracted auth_code value: {auth_code_value}")
                    else:
                        print("auth_code parameter not found in the URL")
                    # The authorization code received from Fyers after the user grants access
                    auth_code = auth_code_value
 
                # Create a session object to handle the Fyers API authentication and token generation
                    session = fyersModel.SessionModel(
                        client_id=client_id,
                        secret_key=secret_key,
                        redirect_uri=redirect_uri,
                        response_type=response_type,
                        grant_type=grant_type
                    )
 
                    # Set the authorization code in the session object
                    session.set_token(auth_code)
 
                    # Generate the access token using the authorization code
                    response = session.generate_token()
                    access_token=response['access_token']
                    return access_token
 
                else:
                    print("NO URI")
account_map = {
        '1': {"name": "Roopa", "client_id": "XXXXXXXXX", "secret_key": "XXXXXXXXX"},
       
    }
 
prompt = "SELECT FYERS ACCOUNT TO GET DATA (1, 2, 3 or 4):\n" + "\n".join(
        [f"{k} - Account {v['name']}" for k, v in account_map.items()]
    )
user_account_selection = simpledialog.askstring("Select FYERS Account", prompt)
if user_account_selection not in account_map:
        raise ValueError("Invalid account selection!")
 
    # Extract account details
account_info = account_map[user_account_selection]
client_id = account_info["client_id"]
secret_key = account_info["secret_key"]
redirect_uri = "https://www.google.com/"
response_type = "code"
grant_type = "authorization_code"
 
file_name_access_token='input_access_token.json'
if os.path.exists(file_name_access_token):
                file_stats_access_token = os.stat(file_name_access_token)
                modified_time = datetime.fromtimestamp(file_stats_access_token .st_mtime).date()
                today_date = date.today()
                if modified_time == today_date:
                   
                    print(f"{file_name_access_token} exists and was modified today ({modified_time}).")
                    with open(file_name_access_token, 'r') as json_file:
                        data_access_token = json.load(json_file)
                        access_token = data_access_token.get('access_token')
                        user_account_num=data_access_token.get('user_account')
                        if access_token and user_account_num==user_account_selection:
                            print(f"Access token found in {file_name_access_token}: {access_token}")
                        else:
                            access_token=get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type)
                            print(f"No access token found in {file_name_access_token}.")
                else:
                    access_token=get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type)
               
else:
    print(f"{file_name_access_token} does not exist.")
    access_token=get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type)
               
data_access_token={'user_account':user_account_selection,'access_token':access_token}
print(data_access_token)
 
file_name_access_token='input_access_token.json'
with open(file_name_access_token, 'w') as json_file:
    json.dump(data_access_token, json_file, indent=4)
 
# Create Fyers client object
fyers = fyersModel.FyersModel(client_id=client_id, token=data_access_token['access_token'], is_async=False, log_path="")
# Download BSE symbol CSV file and save as "BSE_CM_symbol_list.csv"
import pandas as pd
import requests
 
bse_csv_url = "https://public.fyers.in/sym_details/BSE_CM.csv"
bse_csv_filename = "BSE_CM_symbol_list.csv"
 
try:
    bse_df = pd.read_csv(bse_csv_url)
    # Read the 10th column (index 9) data
    if bse_df.shape[1] >= 10:
        tenth_col = bse_df.iloc[:, 9]
        # Find symbols ending with -A or -B
        filtered_symbols = tenth_col[tenth_col.astype(str).str.endswith(('-A', '-B'))]
        print("Symbols in the 10th column ending with -A or -B:")
        print(len(filtered_symbols))
    else:
        print("The CSV does not have a 10th column.")
    symbol_data=bse_df[0:9]
    bse_df.to_csv(bse_csv_filename, index=False)
    print(f"BSE symbol CSV file downloaded and saved as {bse_csv_filename}")
except Exception as e:
    print("Failed to download or save BSE CSV:", e)    
 
 
 
 
 
#time.sleep(120)
def timeconvert(df):
    df["timestamp"]=(pd.to_datetime(df["timestamp"],unit="s", utc=True)
                     .dt.tz_convert('Asia/Kolkata')
                     )
    return df
 
def formating_csv(df_new):
       
       
       
                df_new["DATE"]=pd.to_datetime(df_new["timestamp"]).dt.date
       
       
                df_new["TIME"]=pd.to_datetime(df_new["timestamp"]).dt.time
                df_new["TIME1"] = pd.to_datetime(df_new["TIME"], format="%H:%M:%S")
                df_new["DAY"]=pd.to_datetime(df_new["timestamp"]).dt.day_name("").str.upper()
                # Market open reference
                market_open = pd.to_datetime("09:15:00", format="%H:%M:%S")
               
                # Candle calculation
                # If the time is exactly 00:00:00, set CANDLE_COUNT to 0, else calculate normally
                df_new["CANDLE_COUNT"] = df_new["TIME1"].apply(lambda t: 0 if t.strftime("%H:%M:%S") == "00:00:00" else int((pd.Timedelta(t.strftime("%H:%M:%S")) - pd.Timedelta("09:15:00")).total_seconds() // 60 + 1))
                #df_new["CUMMULATIVE_VOLUME"]=df_new['volume'].cumsum()
                df_new["CATEGORY"]="XX"
                #df_new["TIME_FRAME"]="1_MIN"
               
                #df_new['COM_SYMBOL_NAME']=df_new['COM_SYMBOL_NAME'].str.upper()
                df_new=df_new.rename(columns={"open":"OPEN","high":"HIGH","low":"LOW",'close':"CLOSE","volume":"VOLUME"})
               
                df_new1=df_new[['DATE','DAY','TIME_FRAME','CATEGORY','SYMBOL','CANDLE_COUNT',"TIME","OPEN","HIGH","LOW","CLOSE","VOLUME"]]
                return df_new1
# Loop over the filtered BSE symbols (ending with -A or -B) and fetch historical data for each
import pandas as pd
import time
 
# Assuming filtered_symbols comes from previous code
from datetime import datetime, timedelta
 
# Helper function for date range split
def daterange_chunks(start_date, end_date, chunk=100):
    curr = start_date
    while curr < end_date:
        next_date = min(curr + timedelta(days=chunk-1), end_date)
        yield curr, next_date
        curr = next_date + timedelta(days=1)
 
for symbol in filtered_symbols:
    main_df=pd.DataFrame()
    print(symbol)
    symbol_str = str(symbol).strip()
    if not symbol_str:
        continue
 
    # Set start date (2019-01-01) and end date (today)
    start_date = datetime(2018, 1, 1)
    end_date = datetime.now()
    number_rotate=0
 
    for chunk_start, chunk_end in daterange_chunks(start_date, end_date, chunk=100):
        print("GOING IN THE ROTATION===============================",number_rotate)
        payload = {
            "symbol": f"{symbol_str}",        # use symbol from the filtered list
            "resolution": "1",                # '1' for 1 minute data; 'D' for daily, etc
            "date_format": "1",               # 1 = yyyy-mm-dd format
            "range_from": chunk_start.strftime("%Y-%m-%d"),  # chunked start date
            "range_to": chunk_end.strftime("%Y-%m-%d"),      # chunked end date, max 100 days
            "cont_flag": "1"                  # continuous data if '1'
        }
 
        try:
            history = fyers.history(payload)
            print(f"Historical Data Response for {symbol_str} ({payload['range_from']} to {payload['range_to']}):")
            #print(history)
            if 'candles' in history and history['candles']:
                df = pd.DataFrame(history['candles'], columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["SYMBOL"]=symbol_str.split(":")[1].split("-")[0]
                df["TIME_FRAME"]="1_MIN"
               
                df = timeconvert(df)
                df=formating_csv(df)
                print(df)
            else:
                df=pd.DataFrame()
                print(f"No candle data returned for {symbol_str} ({payload['range_from']} to {payload['range_to']})")
        except Exception as e:
            df=pd.DataFrame()
            print(f"Failed to fetch data for {symbol_str} ({payload['range_from']} to {payload['range_to']}): {e}")
       
        # Optional: sleep to respect API rate limits
        time.sleep(0.30)
        number_rotate=number_rotate+1
        main_df=pd.concat([main_df,df],ignore_index=True)
    #symbol_str=str(symbol_str).split[:][1]
    symbol_name=str(symbol_str).replace(":","")
    symbol_name=symbol_name.replace("-","_")
    print(symbol_str)
    main_df.to_csv(f"{symbol_name}_1MIN.csv")
    time.sleep(1)
 
# Loop over each symbol in the filtered symbol list and retrieve daily (1D) historical data from Fyers.
for symbol in filtered_symbols:
    symbol_str = str(symbol).strip()
    if not symbol_str:
        continue
 
    # For 1D (daily) resolution, Fyers allows up to 366 days per request
    start_date = datetime(2019, 1, 1)
    end_date = datetime.now()
    number_rotate = 0
 
    for chunk_start, chunk_end in daterange_chunks(start_date, end_date, chunk=366):
        print("Getting 1D historical data -- Rotation:", number_rotate)
        payload = {
            "symbol": f"{symbol_str}",
            "resolution": "D",                  # 'D' for daily candles
            "date_format": "1",
            "range_from": chunk_start.strftime("%Y-%m-%d"),
            "range_to": chunk_end.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }
 
        try:
            history = fyers.history(payload)
            print(f"Daily Data for {symbol_str} ({payload['range_from']} to {payload['range_to']}):")
            if 'candles' in history and history['candles']:
                df = pd.DataFrame(history['candles'], columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["SYMBOL"] = symbol_str.split(":")[1].split("-")[0]
                df["TIME_FRAME"] = "1_DAY"
                df = timeconvert(df)
                df = formating_csv(df)
                print(df)
            else:
                df = pd.DataFrame()
                print(f"No daily data for {symbol_str} ({payload['range_from']} to {payload['range_to']})")
        except Exception as e:
            df = pd.DataFrame()
            print(f"Failed to fetch daily data for {symbol_str} ({payload['range_from']} to {payload['range_to']}): {e}")
 
        time.sleep(0.30)
        number_rotate += 1
        main_df = pd.concat([main_df, df], ignore_index=True)
 
    symbol_name = str(symbol_str).replace(":", "")
    symbol_name = symbol_name.replace("-", "_")
    print(f"Finished downloading daily data for: {symbol_str}")
    main_df.to_csv(f"{symbol_name}_1D.csv")
    time.sleep(1)
 
 