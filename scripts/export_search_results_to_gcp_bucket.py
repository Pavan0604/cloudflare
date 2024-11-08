import time
import requests
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime
import argparse
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--splunk-access-token",help="Splunk Access Token")
parser.add_argument("--time-interval",help="Time Interval to query in hours")
parser.add_argument("--gcp-private-key-id",help="GCP private Key id")
parser.add_argument("--gcp-private-key",help="GCP private key")
args = parser.parse_args()

SPLUNK_TOKEN = args.splunk_access_token
TIME_INTERVAL = args.time_interval
GCP_PRIVATE_KEY_ID = args.gcp_private_key_id
GCP_PRIVATE_KEY = args.gcp_private_key

SPLUNK_HOST = "https://clevertap.splunkcloud.com:8089"
GCP_BUCKET_NAME = "splunk_upload"
GCP_FILE_NAME = f"splunk_segment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Define Splunk Search Query
SEARCH_QUERY = f"""
search index=eve* "Done stats Consolidation for" earliest=-{TIME_INTERVAL}h latest=now
| rex "Account (?<account>\d+) : Done stats consolidation for segment id :(?<segment_id>\d+) in (?<time_taken_ms>\d+) milliSecs startTime: (?<start_time>\d+) EndTime: (?<end_time>\d+)"
| where account="1576765056"
| eval start_time_epoch = tonumber(start_time), end_time_epoch = tonumber(end_time)
| where start_time_epoch >= relative_time(now(), "-1d@d+22h")
| eval time_taken_min = time_taken_ms / (1000 * 60)     
| stats sum(time_taken_min) as TimeTakenInMinutes by segment_id account stack host start_time end_time
| sort -TimeTakenInMinutes
"""

service_account_info = {
  "type": "service_account",
  "project_id": "utopian-pier-441005-a2",
  "private_key_id": GCP_PRIVATE_KEY_ID,
  "private_key": GCP_PRIVATE_KEY,
  "client_email": "splunk-upload@utopian-pier-441005-a2.iam.gserviceaccount.com",
  "client_id": "115329117284467900669",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/splunk-upload%40utopian-pier-441005-a2.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

print(f"service_account_info = {service_account_info}")

headers = {
    "Authorization": f"Bearer {SPLUNK_TOKEN}"
}

def trigger_search():
    """Initiates a search job in Splunk Cloud."""
    try:
        url = f"{SPLUNK_HOST}/services/search/jobs"
        data = {
            "search": SEARCH_QUERY,
            "output_mode": "json"
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        job_id = response.json().get("sid")
        if not job_id:
            raise Exception("Failed to retrieve job ID from Splunk response.")
        print(f"Search job triggered with SID: {job_id}")
        return job_id
    except requests.exceptions.RequestException as e:
        print(f"Error triggering search job: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while triggering search job: {e}")
        raise


def check_job_status(job_id):
    """Polls the search job status until completion."""
    try:
        url = f"{SPLUNK_HOST}/services/search/jobs/{job_id}"
        while True:
            response = requests.get(url, headers=headers, params={"output_mode": "json"})
            response.raise_for_status()
            job_status = response.json().get("entry", [{}])[0].get("content", {}).get("dispatchState")
            if not job_status:
                raise Exception("Failed to retrieve job status from Splunk response.")
            print(f"Job status: {job_status}")
            if job_status == "FAILED":
                raise Exception(f"Search job with SID {job_id} failed.")
            if job_status == "DONE":
                break        
            time.sleep(5)
    except requests.exceptions.RequestException as e:
        print(f"Error checking job status: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while checking job status: {e}")
        raise


def retrieve_results(job_id):
    """Fetches the search results in CSV format once the job is complete."""
    try:
        url = f"{SPLUNK_HOST}/services/search/jobs/{job_id}/results"
        response = requests.get(url, headers=headers, params={"output_mode": "csv"})
        response.raise_for_status()
        results_csv = response.text
        if not results_csv:
            raise Exception("No results found in the search job.")
        print("Search results retrieved in CSV format.")
        return results_csv
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving search results: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error while retrieving search results: {e}")
        raise


def upload_to_gcs( bucket_name, filename):
    """Uploads the CSV results to a Google Cloud Storage bucket."""
    try:
        # # Authenticate into GCP using service account credentials
        # credentials = service_account.Credentials.from_service_account_info(service_account_info)
        # storage_client = storage.Client(credentials=credentials, project=service_account_info["project_id"])

        # bucket = storage_client.bucket(bucket_name)
        # blob = bucket.blob(filename)

        # # Upload CSV data
        # blob.upload_from_string(data, content_type="text/csv")
        # print(f"Results uploaded to GCP bucket '{bucket_name}' as '{filename}' in CSV format.")

        content = """This is a sample text file.
                    It contains some content to upload to GCP.
                    You can add more lines here as needed."""

        # Authenticate into GCP using service account credentials
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        storage_client = storage.Client(credentials=credentials, project=service_account_info["project_id"])

        # Create a temporary text file and write content to it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_filename = temp_file.name
            temp_file.write(content.encode('utf-8'))

        # Upload the text file to GCP bucket
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(temp_filename)
        print(f"Text file uploaded to GCP bucket '{bucket_name}' as '{filename}'.")

    except Exception as e:
        print(f"Error uploading results to GCP bucket: {e}")
        raise


def main():
    try:
        # Step 1: Trigger the search job
        # job_id = trigger_search()

        # # Step 2: Poll the job status until it's done
        # check_job_status(job_id)

        # # Step 3: Retrieve search results in CSV format
        # results_csv = retrieve_results(job_id)

        # Step 4: Upload the results to the GCP bucket with a dynamic filename
        upload_to_gcs(GCP_BUCKET_NAME, GCP_FILE_NAME)

    except Exception as e:
        print(f"An error occurred during the process: {e}")


if __name__ == "__main__":
    main()
