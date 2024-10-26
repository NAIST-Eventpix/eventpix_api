import os.path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

sample_event = {
    "summary": "Google I/O 2026",
    "location": "800 Howard St., San Francisco, CA 94103",
    "description": "A chance to hear more about Google's developer products.",
    "start": {
        "dateTime": "2024-10-26T09:00:00-07:00",
        "timeZone": "Japan/Tokyo",
    },
    "end": {
        "dateTime": "2024-10-28T17:00:00-07:00",
        "timeZone": "Japan/Tokyo",
    },
    "recurrence": ["RRULE:FREQ=DAILY;COUNT=2"],
    "attendees": [
        {"email": "lpage@example.com"},
        {"email": "sbrin@example.com"},
    ],
    "reminders": {
        "useDefault": False,
        "overrides": [
            {"method": "email", "minutes": 24 * 60},
            {"method": "popup", "minutes": 10},
        ],
    },
}


class GoogleCalendarAPI:
    def __init__(self) -> None:
        self._service = self.create_service()

    def create_service(self) -> Any:
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)  # type: ignore
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # type: ignore
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials=creds)
            return service

        except HttpError as error:
            print(f"An error occurred: {error}")

        return None

    def insert_event(self, event: dict[str, Any]) -> None:
        self._service.events().insert(calendarId="primary", body=event).execute()


if __name__ == "__main__":
    gc_api = GoogleCalendarAPI()
    gc_api.insert_event(sample_event)
