import boto3
import sys
import re

if len(sys.argv) < 2:
    print("❌ Usage: python trigger_ssm.py '<description>'")
    sys.exit(1)

description = sys.argv[1]
print(f"📄 Description: {description}")


targeting_trigger = "Too few LC cache Redis write operations for TARGETING"
if targeting_trigger not in description:
    print("✅ Alert does not match TARGETING condition. Skipping.")
    sys.exit(0)

region_map = {
    "EU": "eu-west-1",
    "IN": "ap-south-1",
    "US": "us-west-2",
    "SG": "ap-southeast-1",
    "SK": "ap-northeast-2",
    "aps3": "ap-southeast-3",
    "i1": "us-east-1",
    "mec1": "me-central-1"
}

def get_region_from_description(description):
    if "EU" in description:
        return region_map["EU"]
    elif "IN" in description:
        return region_map["IN"]
    elif "US" in description:
        return region_map["US"]
    elif "SG" in description:
        return region_map["SG"]
    elif "SK" in description:
        return region_map["SK"]
    elif "aps3" in description:
        return region_map["aps3"]
    elif "i1" in description:
        return region_map["i1"]
    elif "mec1" in description:
        return region_map["mec1"]
    else:
        print("❌ No matching region found in description.")
        sys.exit(1)

region = get_region_from_description(description)
