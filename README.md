# facebook_scrape
Set of scripts which extract data from facebook.
They are set to use FB Graph API and save the data to CSV, comma-delimited, UTF-8 files.

## Requesites
- Python v3.0
- requests library (the others should be already included)
- FB user/profile with admin access to FB Page (in case of scraping FB Page)
- FB application registered at FB thru which the access token will be obtained/renewed

## Dependencies
- FB Graph API version v2.10 - at the time these scripts were developed and tested.

## Configuration
All scripts use just one main configuration XML file.
This file contains URL address of the Graph API, security data and JSON metadata.
To be able to call the FB Graph API there is a need of ID (User/Profile or Page) and access token.
These can be obtained from the Graph API Explorer: https://developers.facebook.com/tools/explorer
And a long term access token can be obtained by forming and executing this URL: https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=[app_id]&client_secret=[app-secret-code]&fb_exchange_token=[short-term-access-token]
The client data can be found by checking your FB app page.
This long term access token expires in 60 days.
