"""
	File description:
	Extract Posts of a Page feed from FB and exports them to CSV file
	
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
## Define Functions and Constants
############################################################

XML_CONFIG_FILE = r'fb_api_config.xml'
CSV_EXPORT_FILE = r'fb_page_feed.csv'

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
api_url += '/' + XmlGetValue(xmldoc, 'page_feed_url')
api_url += '&access_token=' + XmlGetValue(xmldoc, 'page_access_token')
#print(api_url)
api_mdata = XmlGetValue(xmldoc, 'page_feed_mdata')
#print(api_mdata)

# Prepare CSV
csvfile = open(CSV_EXPORT_FILE, 'w', encoding='utf-8')
csvwriter = csv.DictWriter(  csvfile
                           , fieldnames=['id','object_id','created_time','updated_time','from_id','from_name','message','story','image_url']
                           , dialect = 'excel'
                           , delimiter = ','
                           , lineterminator='\r')
csvwriter.writeheader()

# Prepare regexp: remove new line symbols
rx = '[' + re.escape(''.join(['\r','\r\n'])) + ']'


# Call the API
num_rows = 0
api_res = REQ.get(api_url, data=api_mdata)
if (api_res.ok):
    jRes = api_res.json()['data']
    #print("Number of rows: {0}".format(len(jRes)))
    num_rows = len(jRes)

    for jRow in jRes:
        # Prepare the text fields
        object_id_str = ''
        if ('object_id' in jRow): object_id_str = re.sub(rx, ' ', jRow['object_id'])
        message_str = ''
        if ('message' in jRow): message_str = re.sub(rx, ' ', jRow['message'])
        story_str = ''
        if ('story' in jRow): story_str = re.sub(rx, ' ', jRow['story'])
        image_url_str = ''
        if ('attachments'   in jRow
            and 'data'      in jRow['attachments']
            and 'media'     in jRow['attachments']['data'][0]
            and 'image'     in jRow['attachments']['data'][0]['media']
            and 'src'       in jRow['attachments']['data'][0]['media']['image']):
            image_url_str = re.sub(rx, ' ', jRow['attachments']['data'][0]['media']['image']['src'])

        # Export to CSV
        csvwriter.writerow(
            {
                 'id'           :jRow['id']
                ,'object_id'    :object_id_str
                ,'created_time' :jRow['created_time'][0:19].replace("T", " ")
                ,'updated_time' :jRow['updated_time'][0:19].replace("T", " ")
                ,'from_id'      :jRow['from']['id']
                ,'from_name'    :jRow['from']['name']
                ,'message'      :message_str
                ,'story'        :story_str
                ,'image_url'    :image_url_str
            })
        
else:
    api_res.raise_for_status()

# Close CSV file
csvfile.close()

# Finished
print("Finished. {0} row(s) extracted.".format(num_rows))
