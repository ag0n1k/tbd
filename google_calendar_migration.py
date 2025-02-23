import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pprint import pprint
from tqdm import tqdm
# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    """Authenticate and return the Google Calendar API service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

def move_events_based_on_location(service, source_calendar_id, target_calendar_id, location_filter):
    """Move events from one calendar to another based on location."""
    page_token = None
    while True:
        events = service.events().list(calendarId=source_calendar_id, pageToken=page_token).execute()
        for event in  tqdm(events['items']):
            if 'location' in event and location_filter.lower() in event['location'].lower():
                print(f"Moving event: {event['summary']} (Location: {event['location']})")
                pprint(event)
                id_ = event['id']
                del event['id']
                # Copy event to the target calendar
                service.events().insert(calendarId=target_calendar_id, body=event).execute()
                # Delete event from the source calendar
                service.events().delete(calendarId=source_calendar_id, eventId=id_).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break

def main():
    service = authenticate_google_calendar()

    # Replace with your source and target calendar IDs
    source_calendar_id = 'ag0n1kness@gmail.com'  # 'primary' is the default calendar for the authenticated user
    target_calendar_id = '45f5fa3f7c84c925f36b21e2e6e4e39f3e29255a173574685c1dcc815bc94b2d@group.calendar.google.com'  # Replace with your target calendar ID

    # Replace with the location filter you want to use
    location_filter = 'VKontakte'

    move_events_based_on_location(service, source_calendar_id, target_calendar_id, location_filter)

if __name__ == '__main__':
    main()
