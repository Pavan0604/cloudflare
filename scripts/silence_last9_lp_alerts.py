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

def create_access_token(refresh_token):
    try:
        url = "https://app.last9.io/api/v4/oauth/access_token"
        payload = json.dumps({
            "refresh_token": refresh_token
        })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Cookie': 'last9Org=clevertap; last9Token='
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        if response.status_code == 200:
            res = json.loads(response.text)
            access_token = res["access_token"]
        else:
            logging.error("Unable to retrieve access token, returned status code: " + str(response.status_code))
            sys.exit(0) 
        return access_token
    
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error occurred: {e}")
        sys.exit(0)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        sys.exit(0)
    except KeyError as e:
        logging.error(f"Expected key not found in response: {e}")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Exception: {e}")
        sys.exit(0)

def create_last9_silence(region, access_token):
    try:
        entity_id = ""
        if region == "eu1":
            entity_id = "14d4e8f1-293c-417c-8564-8d23901d4c01"
        elif region == "in1":
            entity_id = "f47d2b45-2aa6-4f65-b378-aa24010bd58a"
        else:
            logging.error("Invalid region " + region + " to silence the alerts")
            sys.exit(0)

        if entity_id != "":
            url = f"https://app.last9.io/api/v4/organizations/clevertap/entities/{entity_id}/alert-rules/snooze"
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
            response.raise_for_status()

            logging.info("Alert successfully silenced")

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error occurred: {e}")
        sys.exit(0)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        sys.exit(0)
    except KeyError as e:
        logging.error(f"Expected key not found in response: {e}")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Exception: {e}")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="Region for which the alerts need to be Silenced", required=True)
    parser.add_argument("--refresh_token", help="refresh token to generate access token", required=True)
    args = parser.parse_args()

    logging.info(f"Arguments parsed: Region - {args.region}")
    access_token = create_access_token(args.refresh_token)
    if access_token:
        create_last9_silence(args.region, access_token)
    else:
        logging.info("Access Token is empty to silence the alerts")
        sys.exit(0)

if __name__ == "__main__":
    main()