"""Try: python helpers/use_api.py  OR  python helpers/use_api.py add"""
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:5000"


def call_api(method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data else {}
    request = Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=5) as response:
            print("HTTP status:", response.status)
            return json.load(response)
    except HTTPError as error:
        print("HTTP error:", error.code, error.read().decode("utf-8"))
    except URLError as error:
        print("Network error:", error.reason, "(is app.py running?)")
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        result = call_api("POST", "/api/notices", {
            "title": "My test notice", "message": "Created by Python API helper.",
            "category": "General"
        })
        print("Created:", result)
    else:
        results = call_api("GET", "/api/notices")
        if results is not None:
            for notice in results:
                print(f"#{notice['id']} - {notice['title']}: {notice['message']}")
