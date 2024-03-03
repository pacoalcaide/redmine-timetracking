import argparse
#from datetime import date
from datetime import datetime
  
def main():
  #hoy=datetime.today()
  hoy_cadena = datetime.today().strftime("%Y-%m-%d")
  
  # recoger los argumentos
  parser = argparse.ArgumentParser(
                  prog='Leer Toggl',
                  description='Lee los datos de Toggl para descargarlos en un fichero CSV')#,
                  #exit_on_error=False)
  parser.add_argument('-v', '--version', help="Version", action='version', version='%(prog)s 0.0.1')
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
  #parser.add_argument('-i', '--inicio', help="Fecha de inicio en formato YYYY-MM-DD (por defecto hoy %(const)s)", 
  #                    nargs='?', const=date.today(), default=date.today(),
  #                    type=lambda s: date.strptime(s, "%Y-%m-%d"))
  #parser.add_argument('-f', '--fin', help="Fecha Fin (por defecto hoy %(const)s)", 
  #                    nargs='?', const=date.today())

  #parser.add_argument('-i', '--fecha_inicio', help="Fecha Inicial", type=fecha_hoy)
  #parser.add_argument('-f', '--fecha_fin', help="Fecha Final", type=fecha_hoy)
  #parser.add_argument('-v', '--verbose',
  #                    action='store_true')
  
  args = parser.parse_args()
  
  print(datetime.strftime(args.inicio,"%Y-%m-%dT%H:%M:%S"),datetime.strftime(args.fin,"%Y-%m-%dT%H:%M:%S"))
  #print(args.fecha_inicio,args.fecha_fin)  
  
if __name__ == "__main__":
    main()