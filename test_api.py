#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.api.jules_api_client import JulesAPIClient

client = JulesAPIClient()
resp = client._request("sessions?pageSize=1")
print("Response keys:", resp.keys())
if 'sessions' in resp:
    print("Number of sessions in first page:", len(resp['sessions']))
    if resp['sessions']:
        print("First session keys:", resp['sessions'][0].keys())
