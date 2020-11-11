#!/usr/local/bin/python3
"""
Author: Sean Hanrahan
shanrahan@vmware.com
Workspace ONE Access script to enumerate all Groups assigned to apps
First iterates through all apps, determines what groups are assigned to each, and then gets the group details
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

#variables to capture group names, track item count
groupNames = []
itemNum = 0

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
    
    # main while loop to iterate through result sets
    while(True):

        catalogItemsReq = session.post(getCatalogItems, headers=headers_catItems, data=json.dumps(payload_getCatalogItems))
        catalogItemsReq.raise_for_status()

        # parse json response
        catalogItems = catalogItemsReq.json()

        # if first iteration, print total expected items
        if itemNum == 0:
            print("Total catalog items: ", catalogItems['totalSize'])
            totalNum = catalogItems['totalSize']


        #STEP 2 - Get Catalog items detail
        # iterate through catalog items in request
        for catItem in catalogItems['items']:
            catUrl = getCatalogDetail + catItem['uuid']

            #get detail for each catalog item
            catalogDetailReq = session.get(catUrl, headers=headers_catDetail)
            catalogDetailReq.raise_for_status()

            # parse JSON response
            catalogDetail = catalogDetailReq.json()

            # increment catalog item count, provide feedback to user
            itemNum += 1
            print("Processing ", itemNum, '/',totalNum, ': ' , catItem['name'])

            #STEP 3 - Get group detail from each catalog item
            #iterate through groups in request
            for group in catalogDetail['items']:
                #get detail for each catalog item, skip anything that comes back not in a group
                if (group['subjectType'] != 'GROUPS'):
                    continue
                grpUrl = getGroupDetail + '&ids=' + group['subjectId']
                groupDetailReq = session.get(grpUrl, headers=headers_groupDetail)
                groupDetailReq.raise_for_status()

                # parse JSON response
                groupDetail = groupDetailReq.json()

                #append to variable / array
                groupNames.append(groupDetail['items'][0]['name'])
        
        #if this is the end of this result-set, iterate to next result-set, otherwise break out of main while loop
        if 'next' in catalogItems['_links']:
            # print('end of current result-set, fetching next')
            getCatalogItems = 'https://' + tenant + catalogItems['_links']['next']['href']
        else:
            break

except HTTPError as http_err:
    print(f'HTTP Error: {http_err}')
except Exception as err:
    print(f'Other error: {err}')

print("Complete!")

# sort & dedupe array
result = [] 
for i in groupNames: 
    if i not in result: 
        result.append(i)

result.sort()

# print result
print('\n******************************************************\n***Unique Groups that are assigned to Catalog Items***\n******************************************************\n')
for item in result:
    print(item)