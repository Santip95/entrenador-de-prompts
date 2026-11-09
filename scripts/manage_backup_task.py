"""Preparar/instalar/consultar/eliminar tarea Windows, sin modificar zona ni políticas."""
import argparse
from datetime import datetime,time,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
NAME='EntrenadorPrompts-Respaldo'
NS='http://schemas.microsoft.com/windows/2004/02/mit/task'

def task_xml(now=None):
    now=now or datetime.now(timezone.utc)
    zone=ZoneInfo('America/Argentina/Cordoba')
    day=now.astimezone(zone).date()
    start=datetime.combine(day,time(2),zone)
    if start<=now:start+=timedelta(days=1)
    # StartBoundary lleva UTC explícito. El sistema conserva su propia zona.
    boundary=start.astimezone(timezone.utc).isoformat().replace('+00:00','Z')
    task=ET.Element('Task',xmlns=NS,version='1.4')
    def child(parent,name,value=None):
        e=ET.SubElement(parent,name)
        if value is not None:e.text=str(value)
        return e
    registration=child(task,'RegistrationInfo');child(registration,'Description','Respaldo local del Entrenador de Prompts: 02:00 America/Argentina/Cordoba; B2 pendiente.')
    triggers=child(task,'Triggers');trigger=child(triggers,'CalendarTrigger');child(trigger,'StartBoundary',boundary);child(trigger,'Enabled','true');child(child(trigger,'ScheduleByDay'),'DaysInterval',1)
    principals=child(task,'Principals');principal=child(principals,'Principal');principal.set('id','Author')
    sid=subprocess.check_output(['whoami','/user','/fo','csv','/nh'],text=True).strip().split(',')[-1].strip('"')
    child(principal,'UserId',sid);child(principal,'LogonType','S4U');child(principal,'RunLevel','LeastPrivilege')
    settings=child(task,'Settings')
    for key,value in [('MultipleInstancesPolicy','IgnoreNew'),('DisallowStartIfOnBatteries','false'),('StopIfGoingOnBatteries','false'),('StartWhenAvailable','true'),('Hidden','true'),('ExecutionTimeLimit','PT1H'),('Enabled','true')]:child(settings,key,value)
    actions=child(task,'Actions');actions.set('Context','Author');exe=child(actions,'Exec');child(exe,'Command',ROOT/'.venv/Scripts/python.exe');child(exe,'Arguments','"'+str(ROOT/'scripts/scheduled_backup.py')+'"');child(exe,'WorkingDirectory',ROOT)
    return ET.tostring(task,encoding='unicode'),boundary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['preparar','validar','instalar','consultar','eliminar']);args=parser.parse_args()
    path=ROOT/'local-data/etapa05/respaldo-task.xml';path.parent.mkdir(exist_ok=True,parents=True)
    if args.action in {'preparar','validar','instalar'}:
        xml,boundary=task_xml();ET.fromstring(xml);path.write_text(xml,encoding='utf-8')
        print('XML preparado. Próximo inicio UTC:',boundary,'(02:00 Cordoba). No se cambió la zona del sistema.')
        if args.action=='preparar':return
        xml_read="[IO.File]::ReadAllText('"+str(path).replace("'","''")+"')"
        if args.action=='validar':command="$service=New-Object -ComObject Schedule.Service; $service.Connect(); $null=$service.GetFolder('\').RegisterTask('"+NAME+"',("+xml_read+"),1,$null,$null,2); Write-Output 'XML validado por Task Scheduler; tarea no registrada.'"
        else:command="Register-ScheduledTask -TaskName '"+NAME+"' -Xml ("+xml_read+") -ErrorAction Stop | Select-Object TaskName,State"
    elif args.action=='consultar':command="Get-ScheduledTask -TaskName '"+NAME+"' -ErrorAction Stop | Get-ScheduledTaskInfo | Select-Object LastRunTime,LastTaskResult,NextRunTime"
    else:command="Unregister-ScheduledTask -TaskName '"+NAME+"' -Confirm:$false -ErrorAction Stop"
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',"$ErrorActionPreference='Stop'; "+command],creationflags=subprocess.CREATE_NO_WINDOW,capture_output=True,text=True)
    if result.returncode:raise SystemExit('No se completó la operación de la tarea. No se solicita ni guarda contraseña de Windows; revisar permisos locales.')
    if args.action=='validar' and 'XML validado' not in result.stdout:
        raise SystemExit('El servicio no confirmó la validación. No se registra como aprobada.')
    print(result.stdout.strip())

if __name__=='__main__':main()
