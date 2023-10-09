import requests
import aiohttp
import asyncio
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("mailmince-76315-firebase-adminsdk-95piz-b8c8d88bb5.json")
    firebase_admin.initialize_app(cred)

async def clearbit_augment(email):
    
    #1. Checking if email in firebase already
   db = firestore.client()
   document_ref = db.collection('record').document(email)
   doc = document_ref.get()

   if doc.exists:
      print(f'Document data: {doc.to_dict()}')
      return
   else:
      url = 'https://person.clearbit.com/v1/people/email/' + email
      api_key = 'sk_c3e44704c248baa7f20aea39c324cfb7'

      async with aiohttp.ClientSession() as session:
         async with session.get(url, auth=aiohttp.BasicAuth(api_key, '')) as response:
            if response.status == 200:
                  data = await response.json()
                  await add_to_firebase(email, data)
            else:
                  print(f"Error {response.status}: {await response.text()}")


async def add_to_firebase(id, record):
    db = firestore.client()
    document_ref = db.collection('record').document(id)
    document_ref.set(record)

def process_email(email):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise

    loop.run_until_complete(clearbit_augment(email))
