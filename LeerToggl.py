#import requests
import json
from base64 import b64encode
import os
import sys
import argparse
from datetime import datetime

# obtener secretos
def get_entornos():
    with open('entorno.json', 'r') as fichero_entorno:
        entornos = json.load(fichero_entorno)

    return entornos
  
def main():
  # variables generales
  hoy_cadena = datetime.today().strftime("%Y-%m-%d")
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
  parser.add_argument('-u',
                      '--usuario',
                      help="Usuario redmine para asignar los tiempos cargados", 
                      required=True),
  parser.add_argument('-e',
                      '--entorno',
                      help="Entorno de Desarrollo (DES) o Producción (PRO) (por defecto Desarrollo \"%(const)s\")", 
                      required=True,
                      nargs='?',
                      choices=['des', 'pro'],
                      const='des'
                      )

  try:
      # extraer argumentos
      args = parser.parse_args()
      
      # extraer los entornos
      entornos = get_entornos()
      
      api_key_toggl = entornos[args.entorno]["API_KEY_TOGGL"]
      api_key_redmine = entornos[args.entorno]["API_KEY_REDMINE"]
      
  except: #argparse.ArgumentError or SystemExit:
      parser.print_help()
      exit(1)
  # Argumentos
  print(f'Argumentos de \"{script_nombre}\": {args.inicio.strftime("%Y-%m-%d")}, {args.fin.strftime("%Y-%m-%d")}, {args.usuario}, {args.entorno}')
  
  # Example usage of the loaded entornos
  print(f"API_KEY_TOGGL: {api_key_toggl}")
  print(f"API_KEY_REDMINE: {api_key_redmine}")

"""
fecha_inicio = "2024-02-25"
fecha_fin = "2024-02-27"
api_token = b"0e435e25de0761bcba5c05a0a755655f:api_token" #en bytes
fichero_salida = "tmp/sal1.json"

# Esta URL parece que solo admite consultar 1 solo día (poniendo el día de antes y el de después)
url="https://api.track.toggl.com/api/v9/me/time_entries?start_date="+fecha_inicio+"&end_date="+fecha_fin

data = requests.get(url, 
                    headers={'content-type' : 'application/json', 
                             'Authorization' : 'Basic %s' %  b64encode(api_token).decode("ascii")})

# incluir la info en un fichero de salida
with open(fichero_salida, "w") as f:
  # Convert data to JSON string with indentation for readability
  formatted_json = json.dumps(data.json(), indent=4)
  # Write the JSON string to the file
  f.write(formatted_json)

print("Datos escritos en \""+fichero_salida+"\" adecuadamente!")
"""

if __name__ == "__main__":
    main()
