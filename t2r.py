import os
import sys
import argparse
import requests
import re
from redminelib import Redmine
from datetime import datetime, timedelta
from base64 import b64encode
from dotenv import dotenv_values

# Function to get time entries from Toggl
def get_toggl_entries(toggl_url_report=None,toggl_api_key=None,inicio=None, fin=None):
  #toggl_url = f"https://api.toggl.com/reports/weekly?workspace_id={toggl_workspace_id}"
  json =  {
            "start_date": inicio.strftime("%Y-%m-%d"), 
            "end_date": fin.strftime("%Y-%m-%d")
          } if inicio and fin else {}
  headers={ 'content-type' : 'application/json', 
            'Authorization' : 'Basic %s' %  b64encode(f"{toggl_api_key}:api_token".encode()).decode("ascii")
          }
  
  """
  import requests
  from base64 import b64encode

  data = requests.post(
  'https://api.track.toggl.com/reports/api/v3/workspace/899743/search/time_entries', 

  json={
  "end_date":"2024-03-22",
  "start_date":"2024-03-22",
  }, 

  headers={ 'content-type' : 'application/json', 
            'Authorization' : 'Basic %s' %  b64encode(f"0e435e25de0761bcba5c05a0a755655f:api_token".encode()).decode("ascii")
  }
  )

  print(data.json())
  """
  
  response = requests.post(toggl_url_report, json=json, headers=headers)
  response.raise_for_status()
  return response.json()

# Extraer info del texto de la descripción toogle_time_entry
# Formato: #999999 - texto - texto - ...
#   * #999999: - es el num. de redmine y no es obligatorio
#     * en su defecto se usará el nombre del proyecto para imputar las horas
#     * sino hay num. redmine, ni proyecto, ese tiempo  no se puede cargar en ningún sitio de Redmine
#   * la última frase de texto tras el último guión se usará como descripción del tiempo 
#     * y sino hay "-", el texto completo
def extract_info(text):
  """
  Extrae el número tras "#" y la última frase tras "-" de una cadena.

  Args:
    text (str): La cadena de texto a procesar.

  Returns:
    tuple: (número, frase)
  """
  # Buscar el número tras "#"
  number_match = re.search(r"#(\d+)", text)
  number = None if number_match is None else int(number_match.group(1))

  # Buscar la última frase tras "-"
  phrase_parts = text.split("-")
  phrase = None if phrase_parts is None else phrase_parts[-1].strip()
  
  return number, phrase

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
  # variables generales
  today = datetime.today()
  hoy_cadena = today.strftime("%Y-%m-%d")
  last_week = today - timedelta(days=7)
  script_nombre = os.path.basename(sys.argv[0])
  
  # recoger los argumentos
  parser = argparse.ArgumentParser(
                      prog=script_nombre,
                      description='Lee los datos de Toggl para descargarlos en un fichero CSV')
  parser.add_argument('-v', 
                      '--version', 
                      help="Version", 
                      action='version', 
                      version='%(prog)s 0.0.1')
  parser.add_argument('-i', 
                      '--inicio', 
                      help="Fecha de INICIO en formato AAAA-MM-DD (por defecto hoy \"%(const)s\")", 
                      required=True,
                      nargs='?',
                      const=hoy_cadena, 
                      type=lambda s: datetime.strptime(s, "%Y-%m-%d"))
  parser.add_argument('-f', 
                      '--fin', 
                      help="Fecha de FIN en formato AAAA-MM-DD (por defecto hoy \"%(const)s\")", 
                      required=True,
                      nargs='?',
                      const=hoy_cadena, 
                      type=lambda s: datetime.strptime(s, "%Y-%m-%d"))
  #parser.add_argument('-u',
  #                    '--usuario',
  #                    help="Usuario redmine para asignar los tiempos cargados", 
  #                    required=True)
  parser.add_argument('-e',
                      '--entorno',
                      help="Entorno de Desarrollo (DES) o Producción (PRO) (por defecto Desarrollo \"%(const)s\")", 
                      required=True,
                      nargs='?',
                      choices=['des', 'pro','ejemplo'],
                      const='des'
                      )
  try:
      # extraer argumentos
      args = parser.parse_args()
  except: #argparse.ArgumentError: #or SystemExit: # type: ignore
      parser.print_help()
      exit(1)
  
  entorno = dotenv_values(f".env.{args.entorno}")        
  
  toggl_url_report = entorno.get("TOGGL_URL_REPORT")
  toggl_api_key = entorno.get("TOGGL_API_KEY")
  
  redmine_url = entorno.get("REDMINE_URL")
  redmine_api_key = entorno.get("REDMINE_API_KEY")
  
  #inicio = args.inicio.strftime("%Y-%m-%d")
  #fin = args.fin.strftime("%Y-%m-%d")

  # Connect to Redmine API
  #redmine = redminelib.Redmine(redmine_url, api_key=redmine_api_key)
  redmine = Redmine(redmine_url, api_key=redmine_api_key)

  # leer de toggl y escribir en loop en redmine

  # Get Toggl time entries for last week
  toggl_entries = get_toggl_entries(toggl_url_report=toggl_url_report, 
                                    toggl_api_key=toggl_api_key, 
                                    inicio=args.inicio, 
                                    fin=args.fin)

  # Loop through Toggl entries and create Redmine time entries
  for entry in toggl_entries:
    # Extract relevant data from Toggl entry
    num_redmine, description = extract_info(entry["description"])
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
        #create_redmine_entry(redmine, project_id, issue_id, hours, start_date)
        print(f"Created Redmine time entry for {description} ({hours} hours)")
    else:
      print(f"Project '{project}' not found in Redmine, skipping entry...")

  print("Finished creating Redmine time entries.")

if __name__ == "__main__":
    main()