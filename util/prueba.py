import os
import sys
import argparse
from datetime import datetime
  
def main():
  hoy_cadena = datetime.today().strftime("%Y-%m-%d")
  script_nombre=os.path.basename(sys.argv[0])
  
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
                      required=True
                      )

  try:
      args = parser.parse_args()
  except argparse.ArgumentError or SystemExit:
      parser.print_help()
      exit(1)
      
  print(f'Argumentos de \"{script_nombre}\": {args.inicio.strftime("%Y-%m-%d")}, {args.fin.strftime("%Y-%m-%d")}, {args.usuario}')


if __name__ == "__main__":
    main()