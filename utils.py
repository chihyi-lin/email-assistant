import base64
import email.utils
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from html.parser import HTMLParser

# --- GMAIL SETUP ---
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Handles OAuth2 authentication and returns the Gmail service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

class HTMLStripper(HTMLParser):
    """Simple helper to strip HTML tags from a string."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    def handle_data(self, d):
        self.text.append(d)
    def get_data(self):
        return ''.join(self.text)

def clean_html(raw_html):
    s = HTMLStripper()
    s.feed(raw_html)
    return s.get_data()

def get_full_email_body(message_payload):
    """Recursively finds and decodes the plain text body from the Gmail payload."""
    # 1. Check if the body is directly in the payload (simple emails)
    body = message_payload.get('body', {}).get('data')
    # 2. If not, look through 'parts' (multi-part emails like newsletters)
    if not body and 'parts' in message_payload:
        for part in message_payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = part.get('body', {}).get('data')
                break
            # If it's another nested multipart, recurse
            elif 'parts' in part:
                body = get_full_email_body(part)
                if body: break
    if body:
        # Decode the base64url encoded string
        return base64.urlsafe_b64decode(body).decode('utf-8')
    return ""


def parse_gmail_message(msg_data):
    """
    Helper to extract metadata and body from a raw Gmail message object.
    """
    payload = msg_data.get('payload', {})
    headers = payload.get('headers', [])

    # 1. Extract Headers
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
    raw_from = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
    raw_date = next((h['value'] for h in headers if h['name'] == 'Date'), "")

    # 2. Parse Sender & Date
    name, addr = email.utils.parseaddr(raw_from)
    try:
        parsed_date = email.utils.parsedate_to_datetime(raw_date)
        formatted_time = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        formatted_time = "Unknown Time"

    # 3. Extract Body
    full_text = get_full_email_body(payload)
    
    return {
        "sender_name": name,
        "sender_email": addr,
        "email_date": formatted_time,
        "email_text": f"Subject: {subject}\n\n{full_text}"
    }


def access_email() -> dict:
    """Fetches the latest unread email and returned the parsed data."""
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me', 
        maxResults=1,
        q="category:primary is:unread"  # change query to fetch more email
        ).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new emails.")
        return {"email_text": "No new emails"}

    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    parsed_data = parse_gmail_message(msg)
    parsed_data["email_id"] = msg_id

    print(f"✅ Successfully parsed email from: {parsed_data['sender_email']}")
    print(f"DEBUG: \n{parsed_data}")
    return parsed_data

if __name__ == "__main__":
    access_email()