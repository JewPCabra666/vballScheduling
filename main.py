from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from scraping import get_schedule, get_schedules, create_calendar_events
from time import sleep
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/calendar.events.readonly',
          'https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.settings.readonly']


def get_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'clientSecrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def create_event():
    # event = {
    #     'summary': 'TEST EVENT',
    #     'location': '2921 Byrdhill Rd, Richmond, VA 23228',
    #     'description': 'super test stuff',
    #     'start': {
    #         'dateTime': '2021-10-07T10:00:00',
    #         'timeZone': 'America/New_York',
    #     },
    #     'end': {
    #         'dateTime': '2021-10-07T11:00:00',
    #         'timeZone': 'America/New_York',
    #     },
    #     'attendees': [
    #         {'email': 'pwnergod411@gmail.com'},
    #     ],
    #     'reminders': {
    #         'useDefault': 'false',
    #         'overrides': [
    #             {'method': 'email', 'minutes': 24 * 60},
    #             {'method': 'popup', 'minutes': 10},
    #         ],
    #     },
    # }

    event = {'summary': 'VBALL - BOMB SQUAD - Week #1 - COURT 10',
             'location': '2921 Byrdhill Rd, Richmond, VA 23228',
             'description': '6:05 PM ON <b>COURT 10</b>\n'
                            '---------\n'
                            'BOMB SQUAD\n'
                            'VS\n'
                            'BULL MOOSE 5.1',
             'start': {'dateTime': '2021-10-08T18:05:00', 'timeZone': 'America/New_York'},
             'end': {'dateTime': '2021-10-08T19:05:00', 'timeZone': 'America/New_York'},
             'attendees': [{'email': 'pwnergod411@gmail.com'}],
             'reminders': {'useDefault': 'false',
                           'overrides': [{'method': 'popup', 'minutes': 600}]}}

    event = service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    print('Event id = %s' % (event.get('id')))
    return event


def read_events():
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 5 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=5, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'], event['id'])


def delete_events(events):
    for event in events:
        print(f'Deleting Event - {event["summary"]}')
        service.events().delete(calendarId='primary', eventId=event['id']).execute()
        print(f'Deleted Event - {event["summary"]}')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    service = get_service()
    e = create_event()
    read_events()
    sleep(10)
    delete_events([e])
    read_events()
