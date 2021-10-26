from __future__ import print_function

import datetime
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from scraping import get_schedules, create_calendar_events

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


def create_events(seasons, teams, attendees):
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
    #         'overrides': [
    #             {'method': 'email', 'minutes': 24 * 60},
    #             {'method': 'popup', 'minutes': 10},
    #         ],
    #     },
    # }
    pre_sent_events = []
    created_events = []
    schedules = get_schedules(seasons, teams)
    # print(schedules)
    for team, schedule in zip(teams, schedules):
        for week in schedule:
            g1, g2 = create_calendar_events(team, week, attendees)
            pre_sent_events.append(g1)
            pre_sent_events.append(g2)

    for event in pre_sent_events:
        created_event = service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()
        created_events.append(created_event)
        print('Event created: %s' % (created_event.get('htmlLink')))
        print('Event id = %s' % (created_event.get('id')))

    return created_events
    # event = service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()
    # print('Event created: %s' % (event.get('htmlLink')))
    # print('Event id = %s' % (event.get('id')))
    # return event


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

    t = ['Hardley any diggity']
    s = ["Coed Wed BBB"]
    created = create_events(seasons=s, teams=t, attendees=["hefter.rebecca17@gmail.com"])
    with open('created_events_wed.json', 'w+') as output_file:
        json.dump(created, output_file)
    # e = create_events()
    # read_events()
    # sleep(10)

    # delete_events(events)
    # read_events()
