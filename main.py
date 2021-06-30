import os
from imbox import Imbox 
import traceback
import email
import imaplib
import os
import logging
import boto3
from botocore.exceptions import ClientError
import os
import time
import uuid
import datetime

class TempImage:
    def __init__(self, basePath="ICAI1", ext=".jpg"):
	      self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
		   	rand=str(uuid.uuid4()), ext=ext)
    def cleanup(self):
	      os.remove(self.path)

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
        print('[ERROR] AWS Upload')
    return True


# enable less secure apps on your google account
# https://myaccount.google.com/lesssecureapps

host = "imap.gmail.com"
username = ""
password = ''
download_folder = "/download_folder"




if not os.path.isdir(download_folder):
    os.makedirs(download_folder, exist_ok=True)
    
mail = Imbox(host, username=username, password=password, ssl=True, ssl_context=None, starttls=False)
messages = mail.messages(unread=True) # defaults to inbox

for (uid, message) in messages:
    mail.mark_seen(uid) # optional, mark message as read

    for idx, attachment in enumerate(message.attachments):
        try:
            att_fn = attachment.get('filename')
            download_path = f"{download_folder}/{att_fn}"
            print(download_path)
            with open(download_path, "wb") as fp:
                fp.write(attachment.get('content').read())

            timestamp = datetime.datetime.now()
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            t = TempImage()
            print("[UPLOAD] {}".format(ts))
            path = "/{base_path}/{timestamp}.png".format(base_path='ICAI', timestamp=ts)
            upload_file(download_path, '', path)
            t.cleanup()
            os.remove(download_path)
	    time.sleep(2)
            
        except:
            print(traceback.print_exc())

mail.logout()

