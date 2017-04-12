#encoding: utf-8

from flask import Flask, render_template, request
import base64
import urllib2
import json

app = Flask(__name__)

tags=["symboling", "normalized-losses", "make", "fuel-type", "aspiration", "num-of-doors", "body-style", "drive-wheels", "engine-location", "wheel-base", "length", "width", "height", "curb-weight", "engine-type", "num-of-cylinders", "engine-size", "fuel-system", "bore", "stroke", "compression-ratio", "horsepower", "peak-rpm", "city-mpg", "highway-mpg", "price"]
default=["0", "0", " "," "," ", " "," "," "," ","0","0","0","0","0"," "," ","0"," ","0","0","0","0","0","0","0","0"]

@app.route('/')
def index():
    return render_template('carPE.html')

@app.route('/uploadImage')
def uploadImage():
    imgData = request.data['img']
    imgData = base64.b64decode(imgData)
    print(type(imgData))
    return

@app.route('/calculate', methods=['GET'])
def calculate():
    global default
    global tags
    result = default
    i = 0
    for tag in tags:
        t = request.args.get(tag)
        if t!='':
            print(len(t))
            result[i] = t
        i+=1
    data ={
        "Inputs":{
            "input1":{
                "ColumnNames": tags,
                "Values": [result]
            },
        },
        "GlobalParameters": {
        }
    }
    body = str.encode(json.dumps(data))
    url = 'https://ussouthcentral.services.azureml.net/workspaces/96f1042c3d7b42428e8dff82cb67cee0/services/383ab927d26f4040a9ea51e7323a32c9/execute?api-version=2.0&details=true'
    api_key = '5ftnmicdaD7qvNIApLHl8mqzHlSy+8oip4o1DUJ7Z6I3fOzGBYiYHEtpys9sfpT/El27cEf5e+09DHXbtS5xuw=='
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    req = urllib2.Request(url, body, headers)
    try:
        response = urllib2.urlopen(req)
        result = json.loads(response.read().decode())
        price=result["Results"]["output1"]["value"]["Values"][0][-1]
        return render_template("result.html", price=price)
    except urllib2.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read().decode()))
        return json.loads(error.read().decode())

@app.route('/faceLogin')
def faceLogin():
    return

if __name__ == '__main__':
    print("hey")
    app.run()
