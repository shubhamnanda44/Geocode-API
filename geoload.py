import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

api_key = False
#print( "If you have a Google Places API key, enter it here")
#print(" api.key = 'AIzaSy___IDByT70'")

if api_key is False:
    api_key = 42
    serviceurl = "http://py4e-data.dr-chuck.net/json?"
else :
    serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"

# Additional detail for urllib
# http.client.HTTPConnection.debuglevel = 1

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS GeographicalLocations (address TEXT, geodata TEXT)''')

# here we are using socket secure layer functioning to ignore SSL certificate errors
contex = ssl.create_default_context()
contex.check_hostname = False
contex.verify_mode = ssl.CERT_NONE

print("use file handling to retrieve each location from where.data file")
fhandle = open("where.data")
counter = 0
for lines in fhandle:
    if counter > 100 :
        print('start retreiving first 100 locations,restart it if u want to retrieve further more locations')
        break

    address = lines.strip() #this is used to retrieve every location in a new row after'' 
    print('')
    cur.execute("SELECT geodata FROM GeographicalLocations WHERE address= ?",
        (memoryview(address.encode()), ))

    try:
        datas = cur.fetchone()[0]
        print("Found in database ",address)
        continue
    except:
        pass

    parameter = dict()
    parameter["address"] = address
    if api_key is not False: parameter['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parameter)

    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=contex)
    datas = uh.read().decode()
    print('Retrieved', len(datas), 'characters', datas[:20].replace('\n', ' '))
    counter = counter + 1

    try:
        js = json.loads(datas)
    except:
        print(datas)  # We print in case unicode causes an error
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print('==== Failure To Retrieve ====')
        print(datas)
        break

    cur.execute('''INSERT INTO GeographicalLocations (address, geodata)
            VALUES ( ?, ? )''', (memoryview(address.encode()), memoryview(datas.encode()) ) )
    conn.commit()
    if counter % 10 == 0 :
        print('Pausing for a bit...')
        time.sleep(3)

print("now start a geodump.py file to read locatins from a database and create a js file and use html file to visualize it on map")
