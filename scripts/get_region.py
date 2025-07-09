import sys
import re

region_map = {
    "EU": "eu-west-1",
    "IN": "ap-south-1",
    "US": "us-west-2",
    "SG": "ap-southeast-1",
    "SK": "ap-northeast-2",
    "APS3": "ap-southeast-3",
    "I1": "us-east-1",
    "MEC1": "me-central-1"
}

def get_region_from_description(description):
    if re.search(r"\[EU\]", description):
        return region_map["EU"]
    elif re.search(r"\[IN\]", description):
        return region_map["IN"]
    elif re.search(r"\[US\]", description):
        return region_map["US"]
    elif re.search(r"\[SG\]", description):
        return region_map["SG"]
    elif re.search(r"\[SK\]", description):
        return region_map["SK"]
    elif re.search(r"\[APS3\]", description):
        return region_map["APS3"]
    elif re.search(r"\[I1\]", description):
        return region_map["I1"]
    elif re.search(r"\[MEC1\]", description):
        return region_map["MEC1"]
    else:
        print("❌ No matching region found in description.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python trigger_ssm.py '<description>'")
        sys.exit(1)

    description = sys.argv[1]
    region = get_region_from_description(description)
    print(region)
