import requests
from datetime import datetime, timedelta

url = "https://hr.talenta.co/api/web/time-sheet/store"

# Read configurations from file.txt
with open('file.txt', 'r') as f:
    lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('//')]

# Parse configuration variables
config_vars = {}
for line in lines:
    if ':' in line:
        key, value = line.split(':', 1)
        config_vars[key.strip()] = value.strip()

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

# Get task configurations (skip config variables)
content = '\n'.join(lines[len(config_vars):])

# Split content into separate configurations (separated by blank lines)
configurations = [config.strip() for config in content.split('\n\n') if config.strip()]

for config in configurations:
    # Split each configuration into lines
    config_lines = config.split('\n')
    
    # Parse configuration
    task_id = int(config_lines[0].strip())
    activity = config_lines[1].strip()
    start_hour = config_lines[2].strip()
    end_hour = config_lines[3].strip()
    start_date = datetime.strptime(config_lines[4].strip(), '%Y-%m-%d')
    end_date = datetime.strptime(config_lines[5].strip(), '%Y-%m-%d')

    # Process each configuration
    print(f"\nProcessing task {task_id}: {activity}")
    for i in range((end_date - start_date).days + 1):
        day = start_date + timedelta(days=i)

        # Skip weekends: Saturday (5) and Sunday (6)
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