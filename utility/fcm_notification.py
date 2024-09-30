# import requests

# def send_fcm_notification(fcm_token, title, body, data):
#     # FCM endpoint
#     url = "https://fcm.googleapis.com/fcm/send"

#     # FCM Server key (replace with your actual key)
#     server_key = 'server_key'

#     # Headers
#     headers = {
#         'Authorization': f'key={server_key}',
#         'Content-Type': 'application/json',
#     }

#     # Payload
#     payload = {
#         "to": fcm_token,  # FCM token of the customer
#         "notification": {
#             "title": title,  # Title of the notification
#             "body": body,    # Body of the notification
#         },
#         "data": data
#     }

#     # Send the POST request
#     response = requests.post(url, headers=headers, json=payload)

#     # Check response
#     if response.status_code == 200:
#         return f"FCM notification sent successfully!"
#     else:
#         return response.content
        
# pip install firebase-admin
# 

import firebase_admin
from firebase_admin import credentials, messaging
import os

# Function to send a notification
def send_fcm_notification(fcm_token, title, body, data):
        
    # # Get the directory of the current script file
    dir_path = os.path.dirname(os.path.realpath(__file__))
  
    # Join the directory path with the JSON filename
    json_file_path = os.path.join(dir_path, 'jomlah-cab-app-firebase-adminsdk-6alay-32a4d2af4c.json')

    print(json_file_path,"yes")
    # Path to your service account key JSON file
    cred = credentials.Certificate(json_file_path)

    # Initialize the Firebase app with the service account credentials
    firebase_admin.initialize_app(cred)

    
    # Create a message
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data,
        token=fcm_token,  # Token of the device you want to send the message to
    )

    # Send the message
    response = messaging.send(message)
    print('Successfully sent message:', response)
    return response

# pip install firebase-admin apscheduler
