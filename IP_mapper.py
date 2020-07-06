import argparse
import re
import sqlite3
import requests
import time
import csv
import geoip2.database
import folium


full_contact_api_key = "YOURKEY"

ap = argparse.ArgumentParser()
ap.add_argument("-d","--database", required=True,help="Path to the SQLite database to analyze.")
args = vars(ap.parse_args())

# To store the emails
ip_list = []

# Simple regex to match email. You can customize accordingly
regex_match = re.compile('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-5]{2})\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-5]{2})$')

'''
Use this script to geolocate IP address. 
Note: You can use any SQLite database as long as it contains IP address. 

'''
# connect to the database
db     = sqlite3.connect(args['database'])
cursor = db.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

# Fetches list of all tables to loop over
tables = cursor.fetchall() 

for table in tables:
    
    print "[*] Scanning table...%s" % table
    
    # To select all records
    cursor.execute("SELECT * FROM %s" % table[0])

    rows = cursor.fetchall()
    
    for row in rows:
        for column in row:
            try:
                ip_matches = regex_match.findall(column)
            except:
                continue
            for match in ip_matches:
                if match not in ip_list:
                    ip_list.append(match)
cursor.close()
db.close()
            
print "[*] Discovered %d matches." % len(ip_list)


# Map object created here
ip_map       = folium.Map()
ip_addresses = []
reader = geoip2.database.Reader("C://Users/Future/Downloads/GeoLite2-City.mmdb")

for ip_addr in ip_list:
	#print(ip_addr)
		if ip_addr in ip_addresses:
			continue
		else:
			ip_addresses.append(ip_addr)
    
    record  = reader.city(ip_addr)
    
    if record.location.latitude:
        
        popup      = folium.Popup(ip_addr)
        marker = folium.Marker([record.location.latitude,record.location.longitude],popup=popup)
        
        ip_map.add_child(marker)

# Saves the map to filename
try:
	ip_map.save("map.html")
	print "[*]  Map successfully created !"
except:
	print "[*]  Map creation failed !"



