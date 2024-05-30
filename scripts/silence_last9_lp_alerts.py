#!/usr/bin/env python3

import argparse
import logging
import sys
import requests
import time
import json

logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

sys.tracebacklimit = 0

def create_last9_silence(region, access_token):
    entity_id = ""
    if region == "eu1":
        entity_id = "14d4e8f1-293c-417c-8564-8d23901d4c01"
    elif region == "in1":
        entity_id = "f47d2b45-2aa6-4f65-b378-aa24010bd58a"
    else:
        logging.info("Invalid region " + region + " to silence the alerts")
        sys.exit(0)

    if entity_id != "":
        url = "https://app.last9.io/api/v4/organizations/clevertap/entities/" + entity_id + "/alert-rules/snooze"
        expiry_time = int(time.time()) + 2400
        payload = json.dumps({
            "until": expiry_time
        })
        headers = {
            'X-LAST9-API-TOKEN': 'Bearer ' + access_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Cookie': 'last9Org=clevertap; last9Token='
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

    else:
        logging.info("Invalid entity ID to silence the alerts")
        sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("--region", help="Region for which the alerts need to be Silenced")
parser.add_argument("--access_token", help="Access token to silence the LP alerts")
args = parser.parse_args()

logging.info('Arguments parsed: Region - ' + args.region)
create_last9_silence(args.region, args.access_token)