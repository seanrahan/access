#!/usr/local/bin/python3
"""
Author: Sean Hanrahan
shanrahan@vmware.com
Workspace ONE Access script to enumerate all apps in an Access Tenant
Requires remote access app defined with clientId and shared secret
install requests and requests_oauthlib using pip3 if you dont have them. For example:
> pip3 install requests
> pip3 install requests_oauthlib
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

# define API call headers/body
headers_catItems = {
    'Accept': 'application/vnd.vmware.horizon.manager.catalog.item.list+json',
    'Content-Type': 'application/vnd.vmware.horizon.manager.catalog.search+json'
}

payload_getCatalogItems = {
    "nameFilter": "",
    "categories": []
}

#variable to init results
firstResult = True

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
    # Get All Catalog Items
    
    # main while loop to iterate through result set
    while(True):

        catalogItemsReq = session.post(getCatalogItems, headers=headers_catItems, data=json.dumps(payload_getCatalogItems))
        catalogItemsReq.raise_for_status()

        # parse json response
        catalogItems = catalogItemsReq.json()

        # if first iteration, print total expected items / header
        if firstResult == True:
            print("Total catalog items: ", catalogItems['totalSize'])
            print("\nTYPE \t\t NAME")
            print("-----------------------------")
            totalNum = catalogItems['totalSize']
            firstResult = False
        
        for catItem in catalogItems['items']:
            print(catItem['catalogItemType'], ": \t", catItem['name'])


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

print("\nComplete!")
