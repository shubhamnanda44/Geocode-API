import sqlite3
import json
import codecs

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('SELECT * FROM GeographicalLocations')
fhandle = codecs.open('where.js', 'w', "utf-8")
fhandle.write("Dataset = [\n")
counter = 0
for rows in cur :
    datas = str(rows[1].decode())
    try: js = json.loads(str(datas))
    except: continue

    if not('status' in js and js['status'] == 'OK') : continue

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]
    if lat == 0 or lng == 0 : continue
    where = js['results'][0]['formatted_address']
    where = where.replace("'", "")
    try :
        print(where, lat, lng)

        counter = counter + 1
        if counter > 1 : fhandle.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+where+"']"
        fhandle.write(output)
    except:
        continue

fhandle.write("\n];\n")
cur.close()
fhandle.close()
print(counter, "records written to where.js")
print("Open where.html to view the data in a browser")

