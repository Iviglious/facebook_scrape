"""
	File description:
	Extract Notifications of a Page from FB and exports them to CSV file
	
	Created by: Iviglious
	Created date: 03 Aug 2017
	
	Description of the input:
	XML_CONFIG_FILE - path and name of the XML file.
	It's controlled by a XML config file, which contains the user data:
	 - User ID
	 - Access Token
	 - FB Graph URLs
	 - etc.
	CSV_EXPORT_FILE - path and name of the CSV file.
"""

import time
import requests as REQ
import json
import csv
import re
from datetime import date, timedelta
from xml.dom import minidom

############################################################
## Define Functions
############################################################

XML_CONFIG_FILE = r'fb_api_config.xml'
CSV_EXPORT_FILE = r'fb_page_notifications.csv'

def XmlGetValue(xmldoc, tag_name):
    """ Function to retrieve the value of XML node """
    return str(xmldoc.getElementsByTagName(tag_name)[0].childNodes[0].nodeValue)


############################################################
## Script Body
############################################################

# Start
print("Started...")

# Get API configuration from XML
xmldoc = minidom.parse(XML_CONFIG_FILE)
api_url  = XmlGetValue(xmldoc, 'root_url')
api_url += '/' + XmlGetValue(xmldoc, 'page_id')
api_url += '/' + XmlGetValue(xmldoc, 'page_notifications_url')
api_url += '&access_token=' + XmlGetValue(xmldoc, 'page_access_token')
#print(api_url)
api_mdata = XmlGetValue(xmldoc, 'page_notifications_mdata')
#print(api_mdata)

# Prepare CSV
csvfile = open(CSV_EXPORT_FILE, 'w', encoding='utf-8')
csvwriter = csv.DictWriter(  csvfile
                           , fieldnames=['id','created_time','updated_time','from_id','from_name','to_id','to_name','title','link','object_id']
                           , dialect = 'excel'
                           , delimiter = ','
                           , lineterminator='\r')
csvwriter.writeheader()


# Call the API
num_rows = 0
api_res = REQ.get(api_url, data=api_mdata)
if (api_res.ok):
    jRes = api_res.json()['data']
    #print("Number of rows: {0}".format(len(jRes)))
    num_rows = len(jRes)

    for jRow in jRes:

        # Export to CSV
        csvwriter.writerow(
            {
                 'id':jRow['id']
                ,'created_time':jRow['created_time'][0:19].replace("T", " ")
                ,'updated_time':jRow['updated_time'][0:19].replace("T", " ")
                ,'from_id': jRow['from']['id']
                ,'from_name':jRow['from']['name']
                ,'to_id':jRow['to']['id']
                ,'to_name':jRow['to']['name']
                ,'title':jRow['title']
                ,'link':jRow['link']
                ,'object_id':jRow['object']['id']
            })
        
else:
    api_res.raise_for_status()

# Close CSV file
csvfile.close()

# Finished
print("Finished. {0} row(s) extracted.".format(num_rows))
