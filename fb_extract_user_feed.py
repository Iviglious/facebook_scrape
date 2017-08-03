"""
	File description:
	Extract Posts of a User feed from FB and exports them to CSV file
	
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
CSV_EXPORT_FILE = r'fb_user_feed.csv'


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
api_url += '/' + XmlGetValue(xmldoc, 'admin_user_id')
api_url += '/' + XmlGetValue(xmldoc, 'user_feed_url')
api_url += '&access_token=' + XmlGetValue(xmldoc, 'access_token')
#print(api_url)
api_mdata = XmlGetValue(xmldoc, 'page_feed_mdata')
#print(api_mdata)

# Prepare CSV
csvfile = open(CSV_EXPORT_FILE, 'w', encoding='utf-8')
csvwriter = csv.DictWriter(  csvfile
                           , fieldnames=['id','created_time','story','message']
                           , dialect = 'excel'
                           , delimiter = ','
                           , lineterminator='\r')
csvwriter.writeheader()

# Prepare regexp: remove new line symbols
rx = '[' + re.escape(''.join(['\r','\r\n'])) + ']'

# Init the main loop
total_rows = 0
start_date = date(2017, 1, 1)
end_date = date.today()
step_days = 30
since_date = start_date
for curr_date in (start_date + timedelta(n) for n in range(step_days, int((end_date - start_date).days), step_days)):

    if (step_days > int((end_date - curr_date).days)):
        curr_date = end_date

    since_dt_str = since_date.strftime("%Y-%m-%d")
    until_dt_str = curr_date.strftime("%Y-%m-%d")

    # Call the API
    num_rows = 0
    api_url_x = api_url.replace("{since_dt_str}", since_dt_str).replace("{until_dt_str}", until_dt_str)
    api_res = REQ.get(api_url_x, data=api_mdata)
    if (api_res.ok):
        jRes = api_res.json()['data']
        #print("Number of rows: {0}".format(len(jRes)))
        num_rows = len(jRes)

        for jRow in jRes:
            # Prepare the text fields
            story_str = ''
            if ('story' in jRow): story_str = re.sub(rx, ' ', jRow['story'])
            msg_str = ''
            if ('message' in jRow): msg_str = re.sub(rx, ' ', jRow['message'])

            # Export to CSV
            csvwriter.writerow(
                {
                     'id'           :jRow['id']
                    ,'created_time' :jRow['created_time'][0:19].replace("T", " ")
                    ,'story'        :story_str
                    ,'message'      :msg_str
                })
        
    else:
        api_res.raise_for_status()

    print("Since {0} until {1}: {2}".format(since_dt_str, until_dt_str, num_rows))

    since_date = curr_date
    total_rows += num_rows
    time.sleep(1) # wait for 1 sec

# Close CSV file
csvfile.close()

# Finished
print("Finished. {0} row(s) extracted.".format(total_rows))
