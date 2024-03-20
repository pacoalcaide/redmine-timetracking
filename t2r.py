import requests
import redminelib
from datetime import datetime, timedelta

# Toggl API credentials
toggl_api_token = "YOUR_TOGGL_API_TOKEN"
toggl_workspace_id = "YOUR_TOGGL_WORKSPACE_ID"

# Redmine API credentials
redmine_url = "YOUR_REDMINE_URL"
redmine_api_key = "YOUR_REDMINE_API_KEY"

# Function to get time entries from Toggl
def get_toggl_entries(since=None, until=None):
  url = f"https://api.toggl.com/reports/weekly?workspace_id={toggl_workspace_id}"
  headers = {"Authorization": f"Basic {toggl_api_token}"}
  params = {"since": since.strftime("%Y-%m-%d"), "until": until.strftime("%Y-%m-%d")} if since and until else {}
  response = requests.get(url, headers=headers, params=params)
  response.raise_for_status()
  return response.json()

# Function to create a Redmine time entry
def create_redmine_entry(redmine, project_id, issue_id, hours, spent_on):
  time_entry = redmine.time_entry.new()
  time_entry.project_id = project_id
  time_entry.issue_id = issue_id
  time_entry.hours = hours
  time_entry.spent_on = spent_on.strftime("%Y-%m-%d")
  time_entry.save()

# Main function
def main():
  # Connect to Redmine API
  redmine = redminelib.Redmine(redmine_url, api_key=redmine_api_key)

  # Get today's date and subtract 7 days to get last week's date
  today = datetime.today()
  last_week = today - timedelta(days=7)

  # Get Toggl time entries for last week
  toggl_entries = get_toggl_entries(since=last_week, until=today)

  # Loop through Toggl entries and create Redmine time entries
  for entry in toggl_entries:
    # Extract relevant data from Toggl entry
    description = entry["description"]
    project = entry["project"]
    start_date = datetime.fromisoformat(entry["start_date"])
    hours = entry["duration"] / (60 * 60)  # Convert duration to hours

    # Find corresponding Redmine project ID (assuming project names match)
    projects = redmine.project.all(name=project)
    if projects:
      project_id = projects[0].id

      # Extract issue ID from description (assuming format "#[issue_id] description")
      match = re.search(r"\[#(\d+)\]", description)
      if match:
        issue_id = int(match.group(1))

        # Create Redmine time entry
        create_redmine_entry(redmine, project_id, issue_id, hours, start_date)
        print(f"Created Redmine time entry for {description} ({hours} hours)")
    else:
      print(f"Project '{project}' not found in Redmine, skipping entry...")

  print("Finished creating Redmine time entries.")

if __name__ == "__main__":
    main()