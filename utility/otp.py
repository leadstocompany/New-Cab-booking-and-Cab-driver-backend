import requests
from django.conf import settings
url = "https://www.fast2sms.com/dev/bulkV2"

def send_otp(otp:int, phone:str):
    print(otp)
    payload = f"variables_values={otp}&route=otp&numbers={phone}"
    headers = {
        'authorization': settings.FAST2SMS,
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)