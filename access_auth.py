#!/usr/local/bin/python3
"""
Author: Sean Hanrahan
shanrahan@vmware.com
utility to obtain bearer token for Workspace ONE Access
"""

client_id = ''
client_secret = ''
tenant = ''
token_url = 'https://' + tenant + '/SAAS/auth/oauthtoken'
auth_url = 'https://' + tenant + '/SAAS/auth/oauth2/authorize'

