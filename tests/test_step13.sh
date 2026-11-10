#!/usr/bin/env bash
# filepath: /workspaces/2027SE_Flask_PWA_API_Rex.L/test_step13.sh
set -euo pipefail

cd /workspaces/2027SE_Flask_PWA_API_Rex.L

echo "Environment checks"
pwd
python3 --version
python3 -c 'from importlib.metadata import version; print("Flask", version("flask"))'

if ! curl --silent --show-error --max-time 5 \
    --output /dev/null http://localhost:3000/; then
    echo "Start the API in another terminal: python3 api.py"
    exit 1
fi

if ! curl --silent --max-time 3 --output /dev/null \
    http://localhost:5000/; then
    echo "PWA is offline; it is not required for this API test."
fi

read -r -s -p "Enter the auth_key from api.py: " auth_key
printf '\n'
[[ -n "$auth_key" ]] || { echo "An API key is required."; exit 1; }

response_file=$(mktemp)
trap 'rm -f "$response_file"' EXIT

payload=$(cat <<JSON
{
  "name": "Authorisation test $(date +%s)",
  "hyperlink": "https://marketplace.visualstudio.com/items?itemName=test.extension",
  "about": "Step 13 authorisation test",
  "image": "https://example.com/icon.png",
  "language": "BASH"
}
JSON
)

failures=0

test_post() {
    local label="$1" expected_status="$2" expected_body="$3"
    shift 3

    # Space requests to respect the POST limit of one per second.
    sleep 1.1

    local status
    status=$(curl --silent --show-error --max-time 10 \
        --output "$response_file" --write-out '%{http_code}' \
        --request POST http://localhost:3000/add_extension \
        --header "Content-Type: application/json" \
        --data "$payload" "$@")

    if [[ "$status" == "$expected_status" ]] &&
        python3 - "$response_file" "$expected_body" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as response:
        actual = json.load(response)
    sys.exit(0 if actual == json.loads(sys.argv[2]) else 1)
except (ValueError, OSError):
    sys.exit(1)
PY
    then
        echo "PASS: $label"
    else
        echo "FAIL: $label — expected HTTP $expected_status, received $status"
        cat "$response_file"
        printf '\n'
        failures=$((failures + 1))
        if [[ "$status" == "429" ]]; then
            echo "Rate limit reached; wait or restart the local API before rerunning."
        fi
    fi
}

test_post "Missing key" 401 '{"error":"Unauthorised"}'
test_post "Incorrect key" 401 '{"error":"Unauthorised"}' \
    --header "Authorisation: ${auth_key}_incorrect"
test_post "Correct key" 201 '{"message":"Extension added successfully"}' \
    --header "Authorisation: $auth_key"

if (( failures > 0 )); then
    echo "$failures test(s) failed."
    exit 1
fi

echo "All three authorisation tests passed."