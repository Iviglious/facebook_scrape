""" Extract all Comments from posts/feed from FB Page """
"""
	File description:
	Extract Comments related to Page posts from FB and exports them to CSV file
	
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
CSV_EXPORT_FILE = r'fb_page_comments.csv'

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
# feed_id
api_url_feed_id  = XmlGetValue(xmldoc, 'root_url')
api_url_feed_id += '/' + XmlGetValue(xmldoc, 'page_id')
api_url_feed_id += '/' + XmlGetValue(xmldoc, 'page_feedid_url')
api_url_feed_id += '&access_token=' + XmlGetValue(xmldoc, 'page_access_token')
#print(api_url_feed_id)
api_mdata_feed_id = XmlGetValue(xmldoc, 'page_feed_mdata')
#print(api_mdata_feed_id)

# comments
api_url_comm  = XmlGetValue(xmldoc, 'root_url')
api_url_comm += '/' + XmlGetValue(xmldoc, 'page_comments_url')
api_url_comm += '&access_token=' + XmlGetValue(xmldoc, 'page_access_token')
#print(api_url_comm)
api_mdata_comm = XmlGetValue(xmldoc, 'page_comments_mdata')
#print(api_mdata_comm)


# Prepare CSV
csvfile = open(CSV_EXPORT_FILE, 'w', encoding='utf-8')
csvwriter = csv.DictWriter(  csvfile
                           , fieldnames=['id','post_id','created_time','from_id','from_name','message','image_url']
                           , dialect = 'excel'
                           , delimiter = ','
                           , lineterminator='\r')
csvwriter.writeheader()

# Prepare regexp: remove new line symbols
rx = '[' + re.escape(''.join(['\r','\r\n'])) + ']'

# Call the Feed API
total_rows = 0
api_res = REQ.get(api_url_feed_id, data=api_mdata_comm)
if (api_res.ok):
    jRes = api_res.json()['data']
    #print("Number of rows (feed): {0}".format(len(jRes)))

    # Feed Loop
    for jRow in jRes:
        # Get post_id
        feed_id = jRow['id']

        # Prepare the Comments API
        api_url_comm_current = api_url_comm.replace('{feed_id}', feed_id)

        # Call the Comments API
        num_rows = 0
        api_res = REQ.get(api_url_comm_current, data=api_mdata_comm)
        if (api_res.ok):
            jRes = api_res.json()
            # Check if there are comments in current post
            if ('comments' not in jRes): continue
            
            num_rows = len(jRes['comments']['data'])
            #print("Number of rows (comments): {0}".format(num_rows))

            feed_id = jRes['id']
            # Comments Loop
            for jRow in jRes['comments']['data']:
                # Prepare the text fields
                message_str = ''
                if ('message' in jRow): message_str = re.sub(rx, ' ', jRow['message'])
                image_url_str = ''
                if ('attachment'    in jRow
                    and 'media'     in jRow['attachment']
                    and 'image'     in jRow['attachment']['media']
                    and 'src'       in jRow['attachment']['media']['image']):
                    image_url_str = re.sub(rx, ' ', jRow['attachment']['media']['image']['src'])

                # Export to CSV
                csvwriter.writerow(
                    {
                         'id'           :jRow['id']
                        ,'post_id'      :feed_id
                        ,'created_time' :jRow['created_time'][0:19].replace("T", " ")
                        ,'from_id'      :jRow['from']['id']
                        ,'from_name'    :jRow['from']['name']
                        ,'message'      :message_str
                        ,'image_url'    :image_url_str
                    })
        
        else:
            api_res.raise_for_status()
        total_rows += num_rows

else:
    api_res.raise_for_status()

# Close CSV file
csvfile.close()

# Finished
print("Finished. {0} row(s) extracted.".format(total_rows))
