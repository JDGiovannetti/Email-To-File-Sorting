import pathlib
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Use pathlib to define paths
token_path = pathlib.Path("C:/PATH/TO/token.json")
client_secrets_path = pathlib.Path("C:/PATH/TO/client_secrets.json")
pdfs_folder = pathlib.Path("C:/PATH/TO/pdfs")

def main():
    # Connect to the gmail API
    creds = authorize()
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)  # initiate service used for all commands

        # Find all msgids matching a specific filter
        msgids = findMessageIds(service)
        # Find all attachment ids connected to the messages found above
        # GET request to ultimately download PDFs requires an id as an argument to search
        attachmentinfo = findAttachmentInfo(msgids, service)
        
        # Return attachment data as a list in base64 format
        attachments = getAttachmentsFromIds(attachmentinfo, service)

        downloadAttachments(attachments)

    except HttpError as error:
        print(f"An error occurred: {error}")

def authorize():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                token_path.unlink()  # delete token.json if refresh fails
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with token_path.open("w") as token:
            token.write(creds.to_json())
    return creds

# Gets message IDs for use in get request to get individual messages we want
# Filters by recipient, subject, and date
def findMessageIds(service, maxResults=5, filter="subject:crew routing sheet newer_than:3d"):
    # Get any messages relating to Routing from my work email
    result = service.users().messages().list(userId='me', maxResults=maxResults, q=f"{filter}").execute()
    ids = []  # save ids to use later for any GET requests
    for item in result["messages"]:
        ids.append(item["id"])
    return ids

# Gets message IDs for use in get request to get the attachments from the messages
def findAttachmentInfo(msgids, service):
    attachmentids = {}  # To avoid OOB errors in case one message has multiple attachments
    for id in msgids:
        msg = service.users().messages().get(userId='me', id=id).execute()
        # Each payload has many parts (e.g. for header, body, attachments). Find only the PDFs
        for parts in msg["payload"]["parts"]:
            if parts["mimeType"] == "application/pdf":
                # gets both the body
                attachmentids[parts["body"]["attachmentId"]] = {"msgid": id, "filename": parts["filename"]}
    return attachmentids

def getAttachmentsFromIds(attachmentinfo, service):
    # Get the data held within the attachments, which gets returned in base64 format
    attachments = dict()  # Hold so that each filename is tied to its PDF data
    for attachmentid, info in attachmentinfo.items():
        result = service.users().messages().attachments().get(userId="me",
                                                              messageId=info["msgid"], id=f"{attachmentid}").execute()
        testfilename = info["filename"]
        testres = result["data"]
        attachments[testfilename] = testres
    print(f"Found {len(attachments)} attachments.")
    return attachments

def downloadAttachments(attachments):
    # Decode the base64 format and save as a pdf
    for name, pdfdata in attachments.items():
        pdfdata = base64.urlsafe_b64decode(pdfdata.encode("UTF-8"))
        # print(pdfdata)
        print(b"Supervise" in pdfdata)
        # Ensures the attachments get put into the pdfs folder
        filepath = pdfs_folder / name
        with filepath.open("wb") as file:
            file.write(pdfdata)

if __name__ == "__main__":
    main()
