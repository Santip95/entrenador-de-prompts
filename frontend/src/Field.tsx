import {cloneElement,createContext,isValidElement,useContext,useId} from 'react';
import type {ReactElement,ReactNode} from 'react';

export const FormErrorContext=createContext(false);

export function Field({label,children}:{label:string;children:ReactNode}){
 const id=useId(),hasError=useContext(FormErrorContext);
 if(!isValidElement(children))return <div className="field"><label htmlFor={id}>{label}</label>{children}</div>;
 const control=children as ReactElement<{id?:string;'aria-describedby'?:string}>;
 const described=[control.props['aria-describedby'],hasError?'form-error':null].filter(Boolean).join(' ').split(' ').filter(Boolean);
 return <div className="field"><label htmlFor={id}>{label}</label>{cloneElement(control,{id,...(described.length?{'aria-describedby':[...new Set(described)].join(' ')}:{})})}</div>;
}
