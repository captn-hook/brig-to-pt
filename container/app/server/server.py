#server on flask that takes a http json post and returns a OK response when done
#                                               ^                                
#                                               |                                
#                                               |                                
#                        request: {"csv": "csv file",                            
#                                  "model": "model link",
#                                  "bucket": "bucket name",
#                                  "folder": "folder name"}

from flask import Flask, request, jsonify
import os
from google.cloud import storage

app = Flask(__name__)

storage_client = storage.Client() #need to set up the service account for this to work

@app.route('/', methods=['POST'])
def index():
    #get the request
    request_json = request.get_json()
    #get the csv file
    csv = request_json['csv']
    #get the model link
    model = request_json['model']

    bucket_name = request_json['bucket']
    folder_name = request_json['folder']
    
    #create folder and download model
    os.system("mkdir model")

    os.system("gcloud storage cp " + model + " model/model.glb")

    #write csv file in same folder
    with open("model/model.csv", "w") as file:
        file.write(csv)

    #run the shell script
    os.system("sh run.sh model")

    #upload the model/output to bucket/model/output
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(folder_name + "/output")
    #upload folder
    blob.upload_from_filename("model/output")

    #force rm the directory
    os.system("rm -rf model")

    #return the response
    return jsonify({"status": "OK"})