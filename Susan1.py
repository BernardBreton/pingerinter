import json
baddata = open("C:\\Users\\bebre\\Documents\\susan.json", "r")
gooddata = open("C:\\Users\\bebre\\Documents\\susangood.json", "r")
theData = baddata.read()
r = json.loads(theData)
types={}
sums={}
for records in r:
    if (records["type"] != "CaperCoreState"):
        #print (records["sessionId"])
        print( records["type"])
        try:
            sums[records["type"]] =sums[records["type"]] +1
        except:
            sums[records["type"]]=1
        if (records["type"]) =="UpdateScale":
           print("->", records['payload']['scaleModal']['scaleDisplay']['scaleStatus'])

print ("-----------------stats---------------------------------")
for k, v in sums.items():
    print(k, v)
