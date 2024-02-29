import requests
import json
from base64 import b64encode

fecha_inicio = "2024-02-25"
fecha_fin = "2024-02-27"
api_token = b"0e435e25de0761bcba5c05a0a755655f:api_token" #en bytes
fichero_salida = "pruebas/sal1.json"

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