from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/blogger']
)

creds = flow.run_local_server(port=8080, open_browser=True)
print("\n✅ SUCCESS!")
print("REFRESH TOKEN:", creds.refresh_token)
