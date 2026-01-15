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
    """Recursively finds and decodes the cleanest version of the email body."""
    parts = message_payload.get('parts', [])
    body_text = ""

    # 1. PRIORITY: Look for Plain Text
    if not parts: # Simple email with no parts
        body_text = message_payload.get('body', {}).get('data', '')
    else:
        # Search for text/plain mimeType first
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body_text = part.get('body', {}).get('data', '')
                break
            elif part['mimeType'] == 'text/html' and not body_text:
                # If we haven't found plain text yet, save the HTML data as a backup
                body_text = part.get('body', {}).get('data', '')
            elif 'parts' in part: # Recurse into nested parts
                body_text = get_full_email_body(part)

    if not body_text:
        return ""

    # 2. Decode from Base64
    decoded_body = base64.urlsafe_b64decode(body_text).decode('utf-8', errors='replace')

    # 3. Clean up: If it looks like HTML, strip the tags
    if "<div" in decoded_body.lower() or "<html" in decoded_body.lower():
        decoded_body = clean_html(decoded_body)

    return decoded_body.strip()


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
    # TODO: --issue: the parsed date is 1 hr earlier-- 
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