import requests
from datetime import datetime, timedelta

url = "https://hr.talenta.co/api/web/time-sheet/store"

# Read all lines, keep blank lines for block splitting
with open('file.txt', 'r') as f:
    lines = [line.rstrip('\n') for line in f]

# Parse configuration variables until the first blank line (skip comments)
config_vars = {}
config_end_idx = 0
for i, line in enumerate(lines):
    if line.lstrip().startswith('//'):
        continue  # skip comment lines
    if ':' in line:
        key, value = line.split(':', 1)
        config_vars[key.strip()] = value.strip()
    if line.strip() == '' and config_vars:
        config_end_idx = i
        break

# Check CSRF token and Cookie
if not config_vars.get('X-Csrf-Token'):
    print("Error: Missing X-Csrf-Token in configuration.")
    exit(1)
if not config_vars.get('Cookie'):
    print("Error: Missing Cookie in configuration.")
    exit(1)

# Set up headers with configuration from file
headers = {
    "Host": "hr.talenta.co",
    "X-Csrf-Token": config_vars.get('X-Csrf-Token', ''),
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Not.A/Brand";v="99", "Chromium";v="136"',
    "Sec-Ch-Ua-Mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, /",
    "Content-Type": "application/json",
    "Origin": "https://hr.talenta.co",
    "Referer": "https://hr.talenta.co/timesheet/time-tracker",
    "Cookie": config_vars.get('Cookie', '')
}

# Get only the blocks after config variables
task_lines = lines[config_end_idx+1:]

# Split blocks by blank line
blocks = []
block = []
for line in task_lines:
    if line.strip() == '':
        if block:
            blocks.append(block)
            block = []
    else:
        block.append(line)
if block:
    blocks.append(block)

for config_lines in blocks:
    # Remove comment lines from each block
    config_lines = [line for line in config_lines if not line.lstrip().startswith('//')]
    if len(config_lines) < 6:
        continue  # skip incomplete blocks

    task_id = int(config_lines[0].strip())
    activity = config_lines[1].strip()
    start_hour = config_lines[2].strip()
    end_hour = config_lines[3].strip()
    start_date = datetime.strptime(config_lines[4].strip(), '%Y-%m-%d')
    end_date = datetime.strptime(config_lines[5].strip(), '%Y-%m-%d')

    print(f"\nProcessing task {task_id}: {activity}")
    for i in range((end_date - start_date).days + 1):
        day = start_date + timedelta(days=i)
        if day.weekday() > 4:
            continue
        date_str = day.strftime("%Y-%m-%d")
        data = {
            "task_id": task_id,
            "activity": activity,
            "start_time": f"{date_str} {start_hour}",
            "end_time": f"{date_str} {end_hour}"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"[✓] Submitted for {date_str}")
        else:
            print(f"[✗] Failed on {date_str} - Status: {response.status_code}")
            print(response.text)
