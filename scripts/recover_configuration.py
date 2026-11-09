"""CLI sin contenidos privados: exportar/verificar/extraer configuración protegida."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.core.config import Settings
from app.operations.configuration_archive import export_configuration,verify_configuration,extract_configuration

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['exportar','verificar','extraer']);parser.add_argument('--destination');parser.add_argument('--file');args=parser.parse_args()
    try:
        settings=Settings()
        if args.action=='exportar':
            if not args.destination:raise ValueError()
            print('Paquete cifrado verificado:',export_configuration(settings,args.destination))
        elif args.action=='verificar':print(json.dumps(verify_configuration(settings,args.file)))
        else:
            if not args.destination:raise ValueError()
            print(json.dumps(extract_configuration(settings,args.file,args.destination)))
    except Exception:raise SystemExit('Operación de configuración no completada. Revisar destino, identidad age y diario; no se muestran secretos ni se reemplaza configuración activa.') from None

if __name__=='__main__':main()
