import requests
import json
from base64 import b64encode
import argparse

def get_secrets():
    with open('secrets.json') as secrets_file:
        secrets = json.load(secrets_file)

    return secrets

def fecha_hoy(string):
    if string
      return string
    else
      return today()
    endif


def main():
    # recoger los argumentos
    parser = argparse.ArgumentParser(
                    prog='Leer Toggl',
                    description='Lee los datos de Toggl',
                    epilog='Para descargarlos en un fichero CSV')

    parser.add_argument('-i', '--fecha-inicio', help="Fecha Inicial", required=True, type=fecha_hoy)
    parser.add_argument('-f', '--fecha-fin', help="Fecha Final", type=fecha_hoy)
    #parser.add_argument('-v', '--verbose',
    #                    action='store_true')
    args = parser.parse_args()
    print(args)
    
    # extraer los secretos
    secrets = get_secrets()

    api_key_toggl = secrets.get("API_KEY_TOGGL")
    api_key_redmine_proyectos = secrets.get("API_KEY_REDMINE_PROYECTOS")
    api_key_redmine_localhost = secrets.get("API_KEY_REDMINE_LOCALHOST")

    # Example usage of the loaded secrets
    print(f"API_KEY_TOGGL: {api_key_toggl}")
    print(f"API_KEY_REDMINE_PROYECTOS: {api_key_redmine_proyectos}")
    print(f"API_KEY_REDMINE_LOCALHOST: {api_key_redmine_localhost}")



if __name__ == "__main__":
    main()



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

