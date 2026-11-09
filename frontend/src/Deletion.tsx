import {useContext,useEffect,useId,useRef,useState} from 'react';
import {FormErrorContext} from './Field';
export const deletionNotice='La eliminación retira los datos del entorno activo. El diario impide reintroducirlos al restaurar. Las copias rotativas deben purgarse en un máximo de 30 días; la verificación en el proveedor externo continúa pendiente.';

export function DeletePractice({busy,onDelete}:{busy:boolean;onDelete:()=>void}){
 const [open,setOpen]=useState(false),[confirmed,setConfirmed]=useState(false),id=useId();
 const toggle=useRef<HTMLButtonElement>(null),first=useRef<HTMLInputElement>(null);
 useEffect(()=>{if(open)first.current?.focus();},[open]);
 function close(){setOpen(false);setConfirmed(false);toggle.current?.focus();}
 return <section><button ref={toggle} disabled={busy} aria-expanded={open} aria-controls={id} onClick={()=>{if(open)close();else{setOpen(true);setConfirmed(false);}}}>Eliminar esta práctica</button><div id={id} hidden={!open} onKeyDown={e=>{if(e.key==='Escape'){e.preventDefault();close();}}}>{open&&<><p>{deletionNotice}</p><p>Se eliminarán todas sus versiones, evaluaciones y alertas. Las otras prácticas se conservan.</p><label><input ref={first} type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/> Confirmo que quiero eliminar toda esta práctica.</label><button disabled={busy||!confirmed} onClick={onDelete}>Confirmar eliminación de práctica</button><button disabled={busy} onClick={close}>Cancelar eliminación de práctica</button></>}</div></section>;
}

export function DeleteAccount({busy,onDelete}:{busy:boolean;onDelete:(password:string)=>void}){
 const [open,setOpen]=useState(false),[confirmed,setConfirmed]=useState(false),[password,setPassword]=useState('');
 const id=useId(),content=useId(),hasError=useContext(FormErrorContext),toggle=useRef<HTMLButtonElement>(null),first=useRef<HTMLInputElement>(null);
 useEffect(()=>{if(open)first.current?.focus();},[open]);
 function close(){setOpen(false);setConfirmed(false);setPassword('');toggle.current?.focus();}
 return <section><button ref={toggle} disabled={busy} aria-expanded={open} aria-controls={content} onClick={()=>{if(open)close();else{setOpen(true);setConfirmed(false);setPassword('');}}}>Eliminar mi cuenta</button><div id={content} hidden={!open} onKeyDown={e=>{if(e.key==='Escape'){e.preventDefault();close();}}}>{open&&<form onSubmit={e=>{e.preventDefault();onDelete(password);}}><p>{deletionNotice}</p><p>Se eliminarán la cuenta, todas sus prácticas, versiones y sesiones. La acción no se puede deshacer desde la aplicación.</p><label htmlFor={id}>Contraseña actual para eliminar la cuenta</label><input id={id} ref={first} type="password" autoComplete="current-password" required aria-describedby={hasError?'form-error':undefined} value={password} onChange={e=>setPassword(e.target.value)}/><label><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/> Confirmo que quiero eliminar mi cuenta y todo su contenido.</label><button disabled={busy||!confirmed}>Confirmar eliminación de cuenta</button><button type="button" disabled={busy} onClick={close}>Cancelar eliminación de cuenta</button></form>}</div></section>;
}
