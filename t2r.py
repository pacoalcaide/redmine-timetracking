"""
Toggl to Redmine

Este script carga en Redmine las entradas de tiempo que se existan en el servicio Toggl

Es necesario preparar el fichero .env.pro con los parámetros correspondientes a tus servicios de Toggle y Redmine.
    * utiliza a modo de ejemplo el fichero .env.ejemplo

La lista de funciones es:

    * get_toggl_entries - recoge las entradas de toggl entre fechas
    * extract_numero - extrae el num redmine de una entrada toggl
    * extract_comentario - extrae el comentario para la entrada de tiempo en redmine
    * create_redmine_entry - crea la entrada de tiempo
    * main - funcion main
"""

import os
import sys
import argparse
import requests
import re

import json
import tempfile
import pandas as pd

from argparse import RawTextHelpFormatter
from io import StringIO, BytesIO
from redminelib import Redmine
from datetime import datetime, timedelta
from base64 import b64encode
from dotenv import dotenv_values

# Mostrar todas las columnas de los dataframe
pd.set_option('display.max_columns', None)

# [ ] aclarar los import que sobran
# [ ] arreglo de los comentarios que sobran
# [ ] hacer log del script 
#       (con libreria "loguru" https://pravash-techie.medium.com/python-libraries-you-should-use-part-1-a68d38d23837)
# [ ] probar la carga de los JSON o CSV directamente en duckdb 
#       (a través de la libreria "dlt" https://pravash-techie.medium.com/python-libraries-you-should-use-part-1-a68d38d23837)
# [ ] montar la versión GUI con Flutter
        # (https://app.raindrop.io/my/0/%23flutter%20/)

# Extraer info del texto de la descripción toogle_time_entry
# Formato: #999999 - texto - texto - ...
#   * #999999: - es el num. de redmine y no es obligatorio
#     * en su defecto se usará el nombre del proyecto para imputar las horas
#     * sino hay num. redmine, ni proyecto, ese tiempo  no se puede cargar en ningún sitio de Redmine
def extract_numero(text: str | None = None) -> int | None:
    """
    Extrae el número tras "#" de una cadena.

    Args:
        text (str): La cadena de texto a procesar.

    Returns:
        numero: (int)
    """
    # Buscar el número tras "#"
    numero_match = re.search(r"#(\d+)", text)
    numero = None if numero_match is None else int(numero_match.group(1))

    return numero

# Extraer info del texto de la descripción toogle_time_entry
# Formato: #999999 - texto - texto - ...
#   * la última frase de texto tras el último guión se usará como descripción del tiempo
#     * y sino hay "-", el texto completo
def extract_comentario(text: str = "") -> str | None:
    """
    Extrae la última frase tras "-" de una cadena.

    Args:
        text (str): La cadena de texto a procesar.

    Returns:
        comentario (str): El comentario para la entrada de texto extraido
    """
    # Buscar la última frase tras " - "
    #   * el separador es "espacio - espacio" para no separar cuando sea el guión de una palabra
    # [x] Devolver None en el comentario del timeentry cuando no viene el guion 
    #   * porque en principio para Redmine no es obligatorio asociado al timeentry a no ser que se configure expresamente
    comentario_parts = text.split(" - ")
    comentario = None if (comentario_parts is None or len(comentario_parts) == 1) else comentario_parts[-1].strip()

    return comentario

# Function to get time entries from Toggl
def get_toggl_entries_csv(  toggl_url_report: str | None = None, 
                            toggl_api_key: str | None = None, 
                            inicio: datetime | None = None, 
                            fin: datetime | None = None
                        ) -> pd.DataFrame:
    
    # [ ] get_toggl_entries: Documentar la función 
    # [X] get_toggl_entries: Ponerle el tipo de dato de salida (es dataframe)
    
    json = (
        {
            "start_date": inicio.strftime("%Y-%m-%d"),
            "end_date": fin.strftime("%Y-%m-%d"),
        } if inicio and fin else {}
    )
    
    headers = {
        "content-type": "application/json",
        "Authorization": "Basic %s"
        % b64encode(f"{toggl_api_key}:api_token".encode()).decode("ascii"),
    }

    response = requests.post(toggl_url_report, json=json, headers=headers)
    response.raise_for_status()

    # Check for successful status code (e.g., 200)
    if response.status_code == 200:
        # Check response content type before parsing
        if response.headers["Content-Type"] == "text/csv":
            # Parse CSV if content type confirms
            csv_data_io = BytesIO(response.content)
            
            # renombramos los nombres de columnas quitando los espacios en blanco delante 
            # y detrás en dichos nombres, y además sustituyendo los espacios en blanco intermedios por "_"
            # dado que python no acepta dichos espacios como válidos en los nombres de columnas de un dataframe
            df = pd.read_csv(csv_data_io).rename(columns=lambda x: x.strip().replace(' ', '_'))
            
            # devolver el panda dataframe 
            return df
            # yield df
        else:
            # Handle unexpected content type
            raise ValueError(
                f"Unexpected response content type: {response.headers['Content-Type']}"
            )
    else:
        # Raise exception with more information about the error
        raise requests.exceptions.RequestException(
            f"Error retrieving report: {response.status_code} - {response.text}"
        )

# Function to create a Redmine time entry
def create_redmine_entry(redmine, project_id, issue_id, spent_on, hours, comentario, actividad):
    """ 
    [ ] create_redmine_entry: definir datos de entrada y ¿de salida?
    [ ] create_redmine_entry: terminar la documentación de la funcion 
    
    Crea la entrada de tiempo en Redmine

    Args:
        ????? text (str): La cadena de texto a procesar.
        redmine, 
        project_id, 
        issue_id, 
        spent_on, 
        hours, 
        comentario, 
        actividad

    Returns:
        ?????  str: (comentario)
    
    Los campos necesarios son ...
        Num Redmine: o Proyecto: (*)
        Usuario (*): ?????
        Fecha (*): 
        Horas (*): 
        Comentario:
        Actividad (*):  
    """

    time_entry = redmine.time_entry.new()
    
    time_entry.project_id = project_id
    time_entry.issue_id = issue_id
    time_entry.spent_on = spent_on.strftime("%Y-%m-%d")
    time_entry.hours = hours
    time_entry.comment = comentario
    time_entry.activity = actividad
    
    time_entry.save()

def set_toggl_tag_entries(  toggl_url_entries: str | None = None, 
                            toggl_api_key    : str | None = None,  
                            time_entry_id    : int | None = None) -> pd.DataFrame:

    data = requests.patch(
        toggl_url_entries, 
        json = { "array":[{
            "op":{"description":"Operation (add/remove/replace)","type":"string"},
            "path":{"description":"The path to the entity to patch (e.g. /description)","type":"string"},
            "value":{"object":{},"description":"The new value for the entity in path."}
            }]}, 
        headers = { 'content-type': 'application/json', 
                    'Authorization' : 'Basic %s' %  b64encode(b"<email>:<password>").decode("ascii")})
    print(data.json())

    json = {"billable":"boolean",
            "created_with":"string",
            "description":"string",
            "duration":"integer",
            "duronly":"boolean",
            "pid":"integer",
            "project_id":"integer",
            "shared_with_user_ids":["integer"],
            "start":"string",
            "start_date":"string",
            "stop":"string",
            "tag_action":"string",
            "tag_ids":["integer"],
            "tags":["string"],
            "task_id":"integer",
            "tid":"integer",
            "uid":"integer",
            "user_id":"integer",
            "wid":"integer",
            "workspace_id":"integer"
            } if time_entry_id else {}

    headers = {
        "content-type": "application/json",
        "Authorization": "Basic %s"
        % b64encode(f"{toggl_api_key}:api_token".encode()).decode("ascii"),
    }

    response = requests.post(toggl_url_entries, json=json, headers=headers)
    response.raise_for_status()

    # Check for successful status code (e.g., 200)
    if response.status_code == 200:
        return
    else:
        # Raise exception with more information about the error
        raise requests.exceptions.RequestException(
            f"Error retrieving report: {response.status_code} - {response.text}"
        )

# Main function
def main():
    # variables generales
    today = datetime.today()
    hoy_cadena = today.strftime("%Y-%m-%d")
    # last_week = today - timedelta(days=7)
    script_nombre = os.path.basename(sys.argv[0])

    # recoger los argumentos
    parser = argparse.ArgumentParser(
        prog = script_nombre,
        description = __doc__, # Carga el docstring del script
        formatter_class = RawTextHelpFormatter # Formato que respeta los \n, etc.
    )
    parser.add_argument(
        "-v", "--version", help="Version", action="version", version="%(prog)s 0.0.1"
    )
    parser.add_argument(
        "-i",
        "--inicio",
        help='Fecha de INICIO en formato AAAA-MM-DD (por defecto hoy "%(const)s")',
        required=True,
        nargs="?",
        const=hoy_cadena,
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )
    parser.add_argument(
        "-f",
        "--fin",
        help='Fecha de FIN en formato AAAA-MM-DD (por defecto hoy "%(const)s")',
        required=True,
        nargs="?",
        const=hoy_cadena,
        type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
    )
    parser.add_argument(
        "-e",
        "--entorno",
        help='Entorno de Desarrollo (DES) o Producción (PRO) (por defecto Desarrollo "%(const)s")',
        required=True,
        nargs="?",
        choices=["des", "pro"],
        const="des",
    )
    try:
        # extraer argumentos
        args = parser.parse_args()
        
        # [ ] controlar que FIN >= INICIO
        # [ ] controlar que FIN - INICIO no es mucho tiempo (ej. ¿varios meses o años?)
        
    except argparse.ArgumentError or SystemExit: # type: ignore
        parser.print_help()
        exit(1)

    # Cargar las variables de entorno
    entorno = dotenv_values(f".env.{args.entorno}")

    # Copiar las variables de entorno
    toggl_url_report = entorno.get("TOGGL_URL_REPORT")
    toggl_api_key = entorno.get("TOGGL_API_KEY")
    redmine_url = entorno.get("REDMINE_URL")
    redmine_api_key = entorno.get("REDMINE_API_KEY")
    # [ ] ¿será necesario añadir el usuario a pesar de tener la API KEY de Redmine?
    #   * porque meter un timeentry en Redmine de Eprinsa el usuario es un campo obligatorio

    # inicio = args.inicio.strftime("%Y-%m-%d")
    # fin = args.fin.strftime("%Y-%m-%d")

    try:
        # Connect to Redmine API
        # redmine = redminelib.Redmine(redmine_url, api_key=redmine_api_key)
        #redmine = Redmine(url = redmine_url, api_key = redmine_api_key)
        redmine = Redmine(url = redmine_url, key = redmine_api_key)

        # Conectar con Toggl API
        # Get Toggl time entries en Pandas dataframe
        toggl_entries = get_toggl_entries_csv(
            toggl_url_report = toggl_url_report,
            toggl_api_key = toggl_api_key,
            inicio = args.inicio,
            fin = args.fin
        )

    except (ValueError, requests.exceptions.RequestException) as e:
        print(f"Error: {e}")
        exit(1)

    # Borramos las columnas que no vamos a necesitar: Billable, Client, Currency, Task, Email, User
    toggl_entries.drop(['Billable', 'Client', 'Currency', 'Task', 'Email', 'User', 'Amount'], axis=1, inplace=True)
    
    # Borramos los registros de tiempo del dataframe de Toggle que ya estan en Redmine (los del tag "en_redmine")
    # etiqueta = toggl_entries['Tags'].str.contains('en_redmine')
    # Durante las pruebas de desarrollo solo usaremos los registros Toggl con la etiqueta "de_prueba", por tanto borraremos el resto
    etiqueta = ~toggl_entries['Tags'].str.contains('de_prueba') # con ~ se consigue la negación
    toggl_entries.drop(toggl_entries[etiqueta].index, inplace=True)
    if toggl_entries.empty:
        print(f'En el tramo de tiempoque va desde {args.inicio.strftime("%Y-%m-%d")} a {args.fin.strftime("%Y-%m-%d")}, \
            no hay datos para enviar a Redmine, quizás porque ya tienen la marca de enviados (etiqueta={etiqueta})')
        exit(1)
    
    # Añadimos colunmnas calculadas para que la futura iteración por cada fila, sea más eficiente 
    # Extraer datos de la descripción
    toggl_entries["redmine_num"] = toggl_entries["Description"].apply(extract_numero)
    toggl_entries["redmine_comentario"] = toggl_entries["Description"].apply(extract_comentario)

    # Consultar los ID de todos los proyectos a los que tengo acceso
    # [ ] Probar a obtener los proyectos con usuarios que no sean "administradores" de Redmine
    redmine_proyectos = pd.DataFrame(
        redmine.project.all(limit=1000).values("id", "name")
        )
    redmine_proyectos.rename(
        columns = { 'id': 'redmine_project_id',
                    'name': 'redmine_project_name'}, 
        inplace=True
        )
    toggl_entries = toggl_entries.merge(
        redmine_proyectos[['redmine_project_name', 'redmine_project_id']], 
        left_on  = 'Project', 
        right_on = 'redmine_project_name', 
        how      = 'left'
        )
    
    print(toggl_entries[['Project', 
                        'Description', 
                        'Duration', 
                        'Tags', 
                        'redmine_project_name', 
                        'redmine_project_id']].head(10))
    
    
    # Consultar los ID de todas las actividades a las que tengo acceso
    # [ ] Probar a obtener las actividades con usuarios que no sean "administradores" de Redmine
    redmine_actividades = pd.DataFrame(
        redmine.enumeration.filter(resource="time_entry_activities").values("id", "name")
        )
    redmine_actividades.rename(
        columns = { 'id': 'redmine_actividad_id',
                    'name': 'redmine_actividad_name'}, 
        inplace=True
        )
    toggl_entries = toggl_entries.merge(
        redmine_actividades[['redmine_actividad_name', 'redmine_actividad_id']], 
        left_on  = 'Tags', 
        right_on = 'redmine_actividad_name', 
        how      = 'left'
        )

    print(toggl_entries[['Project', 
                        'Description', 
                        'Duration', 
                        'Tags', 
                        'redmine_actividad_name', 
                        'redmine_actividad_id'
                        ]].head(10))

    
    # print(toggl_entries[['User', 'Email', 'Client', 'Project', 'Task', 'Description', 'Billable',
                        # 'Start_date', 'Start_time', 'End_date', 'End_time', 'Duration', 'Tags',
                        # 'Currency', 'Amount', 'num_redmine', 'comentario']
                        # ].head(10))
    
    # print(proyectos)
    
    # print(actividades)

    # Recorrer todo el dataframe de toggl
    # for row in toggl_entries:
    for row in toggl_entries.itertuples():
        # Extraer datos de la descripción
        # num_redmine, texto = extract_info(row.Description)
        
        # [ ] que hacer cuando num redmine y proyecto vienen vacios
        #   * devolver por stdout que esa fila no se ha procesato
        #   * ¿quizás más adelante una etiqueta #nrd (no cargado en Redmine) para preparar 2das pasadas de carga de datos de toggl?
        # [ ] que hacer cuando num redmine viene vacio y proyecto relleno
        # [ ] que hacer cuando num redmine viene relleno
        # [x] conseguir que row coja todas las columnas de toggl_entries

        print("\n")

        """ print(f"redmine: {row.num_redmine}")
        print(f"texto: {row.comentario}")
        print(f"proyecto: {row.Project}")

        # Procesamiento específico para cada registro)
        if row.num_redmine is None and row.Project is None:
            print(f"sin redmine ni proyecto:{row}")
        elif row.num_redmine is None and row.Project is not None:
            print(f"sin redmine pero con proyecto:{row}")
        elif row.num_redmine is not None:
            print(f"con redmine:{row}")
        else:
            print("Else final") """

    print("Finished creating Redmine time entries.")

if __name__ == "__main__":
    main()
