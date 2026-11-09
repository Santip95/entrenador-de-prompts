"""Repite recorridos 04/05 con auditoría de accesibilidad e iniciadores de red."""
from pathlib import Path
import json
import sys
import argparse
from datetime import datetime,timezone
from stage06_browser_audit import Audit
import verify_stage04_browser
import verify_stage05_browser

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['flujo','administracion']);args=parser.parse_args()
    folder=Path(__file__).resolve().parents[1]/'local-data/etapa06';folder.mkdir(exist_ok=True,parents=True)
    summary=[]
    for name,module in [('flujo',verify_stage04_browser),('administracion',verify_stage05_browser)]:
        if args.only and name!=args.only:continue
        previous=folder/(name+'-auditoria.json')
        if previous.exists():previous.replace(folder/(name+'-auditoria-anterior-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json'))
        audit=Audit()
        with audit.instrument(module):code=module.main()
        data=audit.save(folder/(name+'-auditoria.json'))
        summary.append({'recorrido':name,'codigo':code,'funcional':code in (0,2),'hallazgos_accesibilidad':data['hallazgos_accesibilidad'],'nf02_aprobado':False})
        print('Auditoria',name,':',len(audit.snapshots),'instantaneas; hallazgos:',data['hallazgos_accesibilidad'],flush=True)
    (folder/'navegadores-resumen.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    return 1 if any(not s['funcional'] or s['hallazgos_accesibilidad'] for s in summary) else 2

if __name__=='__main__':raise SystemExit(main())
