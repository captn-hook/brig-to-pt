#server on flask that takes a http json post and returns a OK response when done
#                                               ^                                
#                                               |                                
#                                               |                                
#                        request: {"csv": "csv file",                            
#                                  "model": "model link",
#                                  "bucket": "bucket name",
#                                  "folder": "folder name"}

from flask import Flask, request, jsonify
import json

import os
#from google.cloud import storage

app = Flask(__name__)

#import projectID from secret

#storage_client = storage.Client(projectID)

@app.route('/', methods=['POST'])
def index():
    #check if request is json
    if request.is_json:
        print("request is json")
        #get json
        try:
            req = request.get_json()
        except:
            print("error getting json")
            print(request.data)
            #request json has a b'' in front of it
            req = json.loads(request.data[1:])

        print(req)
        
        csv = req['csv']
        model = req['model']
        bucket = req['bucket']
        folder = req['folder']

        print("csv: " + csv)
        print("model: " + model)
        print("bucket: " + bucket)
        print("folder: " + folder)
        #create folder and download model
        os.system("mkdir model")

        #os.system("gcloud storage cp " + model + " model/model.glb")
        #temporary, copy default model from /server/Arroyo.glb
        os.system("cp Arroyo.glb model/model.glb")

        #write csv file in same folder
        with open("model/model.csv", "w") as file:
            file.write(csv)

        #run the shell script
        os.system("sh run.sh model")

        print("done?")

        #upload the model/output to bucket/model/output
        #   bucket = storage_client.get_bucket(bucket_name)
        #  blob = bucket.blob(folder_name + "/output")
        #upload folder
        # blob.upload_from_filename("model/output")

        #force rm the directory
        os.system("rm -rf model")

        #return the response
        return jsonify({"response": "OK"}), 200

    else:
        print("request is not json")
        return jsonify({"error": "request is not json"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0')