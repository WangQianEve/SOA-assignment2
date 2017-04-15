#encoding: utf-8

from flask import Flask, render_template, request
import base64
import urllib2
import httplib, urllib
import json

app = Flask(__name__)

tags=["symboling", "normalized-losses", "make", "fuel-type", "aspiration", "num-of-doors", "body-style", "drive-wheels", "engine-location", "wheel-base", "length", "width", "height", "curb-weight", "engine-type", "num-of-cylinders", "engine-size", "fuel-system", "bore", "stroke", "compression-ratio", "horsepower", "peak-rpm", "city-mpg", "highway-mpg", "price"]
default=["0", "0", " "," "," ", " "," "," "," ","0","0","0","0","0"," "," ","0"," ","0","0","0","0","0","0","0","0"]

oct_headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': 'a1b9a236dbd64f519f38810922fc86d1',
}
json_headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': 'a1b9a236dbd64f519f38810922fc86d1',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/carpe')
def carpe():
    return render_template('carPE.html')

@app.route('/login')
def login():
    return render_template('login.html')

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

@app.route('/faceLogin', methods=['POST','GET'])
def faceLogin():
    data = request.form['img']
    bindata = base64.b64decode(data)
    # f = open("bin.png","wb")
    # f.write(bindata)
    # f.close
    detect = json.loads(faceDetection(bindata) )
    faceIDs=[]
    faceId = detect[0]['faceId'].encode('utf-8')
    faceIDs.append(faceId)
    print(faceIDs)

    identify = json.loads(faceIdentify(faceIDs) )
    if(len(identify[0]['candidates']) == 0):
        return "unrecognized"
    else:
        return identify[0]['candidates'][0]["personId"]

def faceDetection(bindata):
    print("Detecting face...")
    params = urllib.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': '',
    })

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, bindata, oct_headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
        return data
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def faceIdentify(faceIDs):
    print("Identifying...")
    params = urllib.urlencode({
    })
    body = {
        "personGroupId":"carpe-group1",
        "faceIds":faceIDs,
        "maxNumOfCandidatesReturned":1,
        "confidenceThreshold": 0.5
    }
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify?%s" % params, str(body), json_headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
        return data
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def trainGroup():
    params = urllib.urlencode({
    })
    print("Training person group...")
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/carpe-group1/train?%s" % params, "", json_headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

if __name__ == '__main__':
    app.run()
