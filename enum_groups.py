#!/usr/local/bin/python3
"""
Author: Sean Hanrahan
shanrahan@vmware.com
script to enumerate all groups by name assigned to apps
"""

import requests
import json
from requests.exceptions import HTTPError
from requests_oauthlib import OAuth2
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

##--- START DATA TO CHANGE ---##
# define auth (uses bearer / access token)
tenant = 'shanrahan.vidmpreview.com' 
clientId = 'python'
sharedSecret = ''
##--- END ---##


#API URL initilization
token_url = 'https://' + tenant + '/SAAS/auth/oauthtoken'
auth_url = 'https://' + tenant + '/SAAS/auth/oauth2/authorize'
login = 'https://'+ tenant + '/SAAS/API/1.0/REST/auth/system/login'
getCatalogItems = 'https://' + tenant + '/SAAS/jersey/manager/api/catalogitems/search'    #POST API call to retrieve all catalog items
getCatalogDetail = 'https://' + tenant + '/SAAS/jersey/manager/api/entitlements/definitions/catalogitems/'   #GET API call to retrieve catalog item detail
getGroupDetail = 'https://' + tenant + '/SAAS/jersey/manager/api/search/lookup?type=Group'     #GeT API call to retrieve group detail

# define API call headers/body
headers_catItems = {
    'Accept': 'application/vnd.vmware.horizon.manager.catalog.item.list+json',
    'Content-Type': 'application/vnd.vmware.horizon.manager.catalog.search+json'
}

headers_catDetail = {
    'Accept': 'application/vnd.vmware.horizon.manager.entitlements.v2.definition.list+json'
}

headers_groupDetail = {
    'Accept': 'application/vnd.vmware.horizon.manager.search.items+json'
}

payload_getCatalogItems = {
    "nameFilter": "",
    "categories": []
}



#variable to capture group names
groupNames = []

### SETUP DONE ###

#initialize session to WS1 Access, get Access token
client = BackendApplicationClient(client_id=clientId)
session = OAuth2Session(client=client)
token = session.fetch_token(token_url=token_url,client_id=id,client_secret=sharedSecret)

# Logic
# 1. get all catalog items
# 2. for each catalog item, get all groups
# 3. for each group get names

try:
    # STEP 1 - Get All Catalog Items
    # enumerate apps in the OG and below
    catalogItemsReq = session.post(getCatalogItems, headers=headers_catItems, data=json.dumps(payload_getCatalogItems))
    catalogItemsReq.raise_for_status()
    
    # check for app list returned
    if (catalogItemsReq.status_code == 204):
        print("EMPTY response")
        exit(1)

    # parse json response
    catalogItems = catalogItemsReq.json()

    #STEP 2 - Get Catalog items detail
    # iterate through catalog items in request
    for catItem in catalogItems['items']:
        catUrl = getCatalogDetail + catItem['uuid']

        #get detail for each catalog item
        catalogDetailReq = session.get(catUrl, headers=headers_catDetail)
        catalogDetailReq.raise_for_status()

        # check for catalog details returned, if empty go to next
        if (catalogDetailReq.status_code == 204):
            print("EMPTY catalog item detail response, moving to next")
            continue

        # parse JSON response
        catalogDetail = catalogDetailReq.json()

        #STEP 3 - Get group detail from each catalog item
        #iterate through groups in request
        for group in catalogDetail['items']:
            #get detail for each catalog item
            grpUrl = getGroupDetail + '&ids=' + group['subjectId']
            groupDetailReq = session.get(grpUrl, headers=headers_groupDetail)
            groupDetailReq.raise_for_status()

            # check for catalog details returned, if no groups go to next
            if (groupDetailReq.status_code == 204):
                print("EMPTY group detail response, moving to next")
                continue

            # parse JSON response
            groupDetail = groupDetailReq.json()

            #append to variable / array
            groupNames.append(groupDetail['items'][0]['name'])


except HTTPError as http_err:
    print(f'HTTP Error: {http_err}')
except Exception as err:
    print(f'Other error: {err}')

# sort & dedupe array
result = [] 
for i in groupNames: 
    if i not in result: 
        result.append(i)

result.sort()

# print result
print('***Unique Groups that are assigned to Catalog Items***\n', result)