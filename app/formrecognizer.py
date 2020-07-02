import json,os
import time
from requests import get, post
import pandas as pd
from sqlalchemy import create_engine
import urllib
from flask import current_app as app
from flask import send_file

#form recognizer class with static methods to perform functions
class FormRecognize():
    
    #method to send file to azure form recognizer endpoint
    @staticmethod
    def analyze(source,file_type):
        
        if (file_type == 'pdf'):
            content_type = 'application/pdf'
        elif (file_type == 'jpg' or file_type == 'jpeg'):
            content_type == 'image/jpeg'
        elif (file_type == 'tiff'):
            content_type == 'image/tiff'
        
        params = {
            "includeTextDetails": True
        }

        headers = {
        
            'Content-Type': content_type,
            'Ocp-Apim-Subscription-Key': app.config['APIM_KEY'],
        }

        with open(source, "rb") as f:
            data_bytes = f.read()

        try:
            resp = post(url = app.config['POST_URL'], data = data_bytes, headers = headers, params = params)
            if resp.status_code != 202:
                print("POST analyze failed:\n%s" % json.dumps(resp.json()))
                quit()
            # print("POST analyze succeeded:\n%s" % resp.headers)
            get_url = resp.headers["operation-location"]
            return get_url
        except Exception as e:
            print("POST analyze failed:\n%s" % str(e))
            quit() 

    #method to get analyzed results in json from azure form recognizer endpoint
    @staticmethod
    def analyze_results(get_url):
        n_tries = 15
        n_try = 1
        wait_sec = 5
        max_wait_sec = 5
        while n_try < n_tries:
            try:
                resp = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": app.config['APIM_KEY']})
                resp_json = resp.json()
                if resp.status_code != 200:
                    print("GET analyze results failed:\n%s" % json.dumps(resp_json))
                    quit()
                status = resp_json["status"]
                if status == "succeeded":
                    with open('result.json', 'w') as outfile:
                        json.dump(resp_json, outfile)
                    break
                if status == "failed":
                    print("Analysis failed:\n%s" % json.dumps(resp_json))
                    quit()
                # Analysis still running. Wait and retry.
                time.sleep(wait_sec)
                n_try += 1
                wait_sec = min(2*wait_sec, max_wait_sec)     
            except Exception as e:
                msg = "GET analyze results failed:\n%s" % str(e)
                print(msg)
                quit()
        print("Analyze operation did not complete within the allocated time.")

    #helper function for json parsing
    @staticmethod
    def extract_value(value):
        if value['type'] == 'number':
            return value['text']
        elif value['type'] == 'string':
            return value['valueString']
        # elif value['type'] == 'date':
        #     return value['valueDate']            
        elif value['type'] == 'time':
            return value['valueTime']
        elif value['type'] == 'phoneNumber':
            return value['valuePhoneNumber']
        elif value['type'] == 'object':
            objectKeys = value['valueObject'].keys()
            item_info = "" 
            for ok in objectKeys:
                item_info += ok + ":" + FormRecognize.extract_value(value['valueObject'][ok]) + " "
            return item_info
        elif value['type'] == 'array':
            itemInfo = ""
            for item in value["valueArray"]:
                itemInfo += FormRecognize.extract_value(item) + "; "
            return itemInfo[:-3] # ; 
        else:
            print("Skipping Unsupported Type")

    #takes json input, parses and converts it into pandas Dataframe
    @staticmethod
    def parseresults():
        # confidence_threshold = 0
        file_path = "result.json"
        with open(file_path) as f:
            data = json.loads(f.read())
            docResults = data["analyzeResult"]["documentResults"]
            docs = []
            for doc in docResults:
                fields = doc['fields']
                docs.append({key:FormRecognize.extract_value(fields[key]) for key in fields.keys()}) 
        cleandata = pd.DataFrame(docs)
        return cleandata

   
    #method to save data in different formats
    @staticmethod
    def save_data(file_type,data):
        if (file_type == "csv"):
            data.to_csv(r"form_data.csv",index=False, mode='a',header=not os.path.exists("form_data.csv"))
        elif (file_type == "sql"):
            quoted = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=DESKTOP-GBKRM5T;DATABASE=FormData")
            engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
            data.to_sql('Form_1', schema='dbo', con = engine, chunksize=200, index=False, if_exists='append')
        elif (file_type == "xlsx"):
            data.to_excel("form_data.xlsx",index=False,header=True)
        elif (file_type == "txt"):
            data.to_csv(r"form_data.txt", header=not os.path.exists("form_data.txt"), index=None, sep=' ', mode='a')
