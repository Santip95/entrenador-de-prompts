"""Aplicación/persistencia de prácticas. El motor puro no carga catálogos."""
from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from copy import deepcopy
import base64
import hashlib
import hmac
import json
import secrets
from uuid import UUID, uuid4

from app.db.practices import sql

from app.application.access import AccessError, AccessService
from app.core.config import ROOT_DIR
from app.domain.evaluation import (CODES, MOTOR_VERSION, Evaluation, EvaluationContext,
    canonical, compare, confirm, evaluate, normalize_draft, normalize_objective,
    review_objective, validate_configuration, ratio)

CATALOG_LOCK = 90404  # Publicadores de etapa 05 deben usar el mismo lock exclusivo.
LIMITS = ["El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.",
          "Estos patrones no detectan toda la información sensible."]


def hashed(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def conflict():
    raise AccessError(409, "revision_desactualizada", "La revisión venció o los datos cambiaron. Revisá nuevamente.")


class PracticeService:
    def __init__(self, settings):
        self.settings = settings
        self.catalogs = json.loads((ROOT_DIR / "seeds/catalogs.json").read_text(encoding="utf-8"))
        self.key = settings.review_signing_key.get_secret_value().encode()
        self.fingerprint = settings.alert_fingerprint_key.get_secret_value().encode()

    def context(self, user, practice):
        return EvaluationContext(self.key, self.fingerprint, str(user["id"]), str(practice), str(self.settings.alert_fingerprint_key_version))

    def catalog(self, c, challenge_id=None, own=None, *, published=True):
        sql(c, 'catalog_reloj_bloqueo', key=CATALOG_LOCK)
        criteria = {r["codigo"]: dict(r) for r in sql(c, 'catalog_criterio').mappings()}
        rules = [dict(r, id=str(r["id"])) for r in sql(c, 'catalog_regla').mappings()]
        challenge = None
        if challenge_id:
            row = sql(c, 'catalog_desafio', id=challenge_id).mappings().first()
            if not row:
                raise AccessError(404, "no_encontrado", "Desafío no encontrado.")
            if published and row["estado"] != "publicado":
                raise AccessError(409, "desafio_inactivo", "El desafío no admite nuevas versiones por el momento.")
            challenge = dict(row, id=str(row["id"]))
            config = {r["codigo"]: {**r["configuracion"], "obligatorio": r["obligatorio"]} for r in sql(c, 'catalog_desafio_criterio', id=challenge_id).mappings()}
        else:
            config = deepcopy(own)
        presentation = {k: {"nombre": v["nombre"], "descripcion": v["descripcion"]} for k,v in criteria.items()}
        if published:
            validate_configuration(config, rules, self.catalogs, presentation)
        return {"configuracion": config, "reglas": rules, "criterios": presentation, "desafio": challenge}

    def own_configuration(self, applicability):
        if type(applicability) is not dict or set(applicability) != {"C2", "C3", "C4"} or any(type(v) is not bool for v in applicability.values()):
            raise AccessError(422, "aplicabilidad_invalida", "Elegí la aplicabilidad de contexto, destinatario y restricciones.")
        parameters = {"C1": {"acciones_permitidas": list(self.catalogs["acciones"])},
                      "C2": {"campos_requeridos": [], "exigir_texto": True}, "C3": {},
                      "C4": {"selecciones_requeridas": [], "exigir_texto": True},
                      "C5": {"tipos_permitidos": list(self.catalogs["formatos"]), "exigir_detalle": False}, "C6": {}}
        return {code: {"aplica": applicability.get(code, True), "obligatorio": applicability.get(code, True), "parametros": parameters[code]} for code in CODES}

    def start_data(self, data):
        challenge = data.get("desafio_id")
        if challenge:
            if data.get("objetivo") is not None or data.get("aplicabilidad") is not None:
                raise AccessError(422, "origen_invalido", "Elegí un desafío o un objetivo propio, no ambos.")
            return {"desafio_id": str(challenge), "objetivo": None, "modo": data["modo"], "configuracion_propia": None}
        objective = normalize_objective(data.get("objetivo"))
        return {"desafio_id": None, "objetivo": objective, "modo": data["modo"], "configuracion_propia": self.own_configuration(data.get("aplicabilidad"))}

    def issue(self, c, operation, user, practice, content, configuration):
        now = sql(c, 'issue_reloj_bloqueo').scalar()
        payload = {"op": operation, "uid": str(user["id"]), "pid": str(practice), "contenido": hashed(content),
                   "config": hashed(configuration), "clave_version": self.settings.alert_fingerprint_key_version,
                   "exp": int((now + timedelta(minutes=10)).timestamp()), "nonce": secrets.token_hex(16)}
        raw = base64.urlsafe_b64encode(canonical(payload).encode()).rstrip(b"=").decode()
        signature = hmac.new(self.key, raw.encode(), hashlib.sha256).hexdigest()
        return raw + "." + signature, datetime.fromtimestamp(payload["exp"], timezone.utc)

    def check(self, c, token, operation, user, practice, content, configuration):
        try:
            raw, signature = token.split(".")
            if not hmac.compare_digest(hmac.new(self.key, raw.encode(), hashlib.sha256).hexdigest(), signature):
                conflict()
            data = json.loads(base64.urlsafe_b64decode(raw + "="*(-len(raw)%4)))
            valid = data["op"] == operation and data["uid"] == str(user["id"]) and (practice is None or data["pid"] == str(practice))
            valid = valid and data["contenido"] == hashed(content) and data["config"] == hashed(configuration)
            valid = valid and data["clave_version"] == self.settings.alert_fingerprint_key_version
            valid = valid and data["exp"] > sql(c, 'issue_reloj_bloqueo').scalar().timestamp()
            UUID(data["pid"])
            if not valid:
                conflict()
            return data
        except AccessError:
            raise
        except (ValueError, TypeError, KeyError, UnicodeError):
            conflict()

    def objective_review(self, user, pid, content, catalog):
        if content["objetivo"] is None:
            return None
        active, effective = validate_configuration(catalog["configuracion"], catalog["reglas"], self.catalogs, catalog["criterios"])
        return review_objective(content["objetivo"], effective["C6"]["detectores_activos"], context=self.context(user, pid))

    def prepare(self, c, user, data):
        content = self.start_data(data)
        catalog = self.catalog(c, content["desafio_id"], content["configuracion_propia"])
        pid = uuid4()
        review = self.objective_review(user, pid, content, catalog)
        token, expiry = self.issue(c, "inicio", user, pid, content, catalog)
        return {"preview": True, "coincidencias": review.matches if review else [], "token_inicio": token, "vence_en": expiry, "configuracion": catalog, "catalogos": self.catalogs, "limites": LIMITS}

    def create(self, c, user, data):
        content = self.start_data(data)
        selected = data["coincidencias_confirmadas"]
        entry_hash = hashed(content)
        existing = sql(c, 'create_practica_3', uid=user["id"], rid=data["request_id"]).mappings().first()
        if existing:
            if existing["entrada_hash"] != entry_hash:
                conflict()
            return self.practice(c, user, existing["id"]), False
        catalog = self.catalog(c, content["desafio_id"], content["configuracion_propia"])
        payload = self.check(c, data["token_inicio"], "inicio", user, None, content, catalog)
        pid = UUID(payload["pid"])
        review = self.objective_review(user, pid, content, catalog)
        keys = {m["clave"] for m in review.matches} if review else set()
        if set(selected) != keys or len(set(selected)) != len(selected):
            conflict()
        if sql(c, 'create_practica_2', id=pid).first():
            conflict()
        metadata = [{"tipo": m["tipo"], "campo": m["campo"], "confirmada": True} for m in review.matches] if review else []
        sql(c, 'create_practica',
            id=pid, uid=user["id"], challenge=content["desafio_id"], objective=content["objetivo"], mode=content["modo"],
            config=canonical(content["configuracion_propia"]) if content["configuracion_propia"] is not None else None,
            rid=data["request_id"], hash=entry_hash, review=canonical({"coincidencias":metadata,"confirmado_en":sql(c,'issue_reloj_bloqueo').scalar().isoformat()}))
        return self.practice(c, user, pid), True

    def practice(self, c, user, pid):
        p = dict(AccessService.owned(c, user, "practica", pid))
        catalog = self.catalog(c, p["desafio_id"], p["configuracion_propia"], published=False)
        return {k: p[k] for k in ("id","modo","objetivo","desafio_id","configuracion_propia","creado_en","actualizado_en","revision_inicio")} | {"configuracion":catalog,"catalogos":self.catalogs}

    def evaluate(self, user, practice, draft, catalog, selected=None):
        if draft["modo"] != practice["modo"]:
            raise AccessError(422, "modo_inmutable", "El modo de esta práctica no puede cambiar.")
        args = (draft,catalog["configuracion"],catalog["reglas"],self.catalogs,catalog["criterios"])
        kwargs = {"context":self.context(user,practice["id"]),"objective":practice["objetivo"]}
        result = evaluate(*args, **kwargs)
        if selected is not None:
            if set(selected) != {m["clave"] for m in result.matches} or len(selected)!=len(set(selected)):
                conflict()
            result = evaluate(*args, **kwargs, confirmation=confirm(result,selected))
        return result

    def review(self, c, user, pid, draft):
        p = AccessService.owned(c,user,"practica",pid)
        catalog = self.catalog(c,p["desafio_id"],p["configuracion_propia"])
        draft = normalize_draft(draft,self.catalogs)
        result = self.evaluate(user,p,draft,catalog)
        token, expiry = self.issue(c,"revision",user,pid,draft,catalog)
        return result.public() | {"preview":True,"token_revision":token,"vence_en":expiry,"configuracion":catalog,"limites":LIMITS}

    def save(self, c, user, pid, data):
        p = AccessService.owned(c,user,"practica",pid)
        draft = normalize_draft(data["borrador"],self.catalogs)
        entry_hash = hashed(draft)
        existing = sql(c,'save_version_prompt_3',id=pid,rid=data["request_id"]).mappings().first()
        if existing:
            if existing["contenido_hash"] != entry_hash:
                conflict()
            return self.version(c,user,existing["id"]),False
        catalog = self.catalog(c,p["desafio_id"],p["configuracion_propia"])
        sql(c,'save_practica',id=pid)
        self.check(c,data["token_revision"],"revision",user,pid,draft,catalog)
        result = self.evaluate(user,p,draft,catalog,data["coincidencias_confirmadas"])
        if not result.saveable:
            raise AccessError(422,"borrador_vacio","El prompt no puede estar completamente vacío.")
        vid,eid = uuid4(),uuid4()
        number = sql(c,'save_version_prompt_2',id=pid).scalar()
        sql(c,'save_version_prompt', id=vid,pid=pid,n=number,components=canonical(result.components),text=result.text,confirmed=draft["componentes_confirmados"],rid=data["request_id"],hash=entry_hash)
        snapshot = deepcopy(result.snapshot) | {"desafio":catalog["desafio"],"clave_huellas":int(result.key_version)}
        sql(c,'save_evaluacion',id=eid,vid=vid,snapshot=canonical(snapshot),signature=result.signature,motor=MOTOR_VERSION,k=result.fulfilled,a=result.applicable)
        for r in result.results:
            cid = sql(c,'save_criterio',code=r["criterio_codigo"]).scalar()
            sql(c,'save_resultado',eid=eid,cid=cid,rid=r["regla_id"],state=r["estado"],evidence=canonical(r["evidencia"]),condition=r["condicion_esperada"],message=r["mensaje"],action=r["accion_sugerida"])
        for ordinal,(m,fingerprint) in enumerate(zip(result.matches,result.fingerprints),1):
            sql(c,'save_alerta_sensible', id=uuid4(),vid=vid,type=m["tipo"],field=m["campo"],hash=fingerprint,key=int(result.key_version),ordinal=ordinal)
        sql(c,'save_practica_2',id=pid)
        return self.version(c,user,vid),True

    def historical(self,c,user,vid):
        v = dict(AccessService.owned(c,user,"version",vid))
        e = sql(c,'historical_evaluacion',id=vid).mappings().one()
        results = [dict(r, nombre=e["snapshot"]["criterios"][r["criterio_codigo"]]["nombre"],regla_version=e["snapshot"]["reglas"].get(r["criterio_codigo"],{}).get("version") if r["regla_id"] else None) for r in sql(c,'historical_resultado',id=e["id"]).mappings()]
        alerts = list(sql(c,'historical_alerta_sensible',id=vid).mappings())
        matches = tuple({"clave":str(a["id"]),"tipo":a["tipo"],"campo":a["campo"],"mensaje":"Coincidencia revisada y confirmada; no garantiza seguridad.","confirmada":True} for a in alerts)
        versions = {a["clave_version"] for a in alerts}
        # Guardar versión de huellas también para evaluaciones sin coincidencias.
        key_version = str(e["snapshot"].get("clave_huellas",next(iter(versions),1)))
        result = Evaluation(v["texto"],v["componentes"],tuple(results),matches,e["snapshot"],e["firma_comparacion"],"",tuple(a["huella"] for a in alerts),key_version,(str(user["id"]),str(v["practica_id"])),True)
        return v,e,result

    def version(self,c,user,vid):
        v,e,result = self.historical(c,user,vid)
        return result.public() | {"motor_version":e["motor_version"],"preview":False,"id":v["id"],"practica_id":v["practica_id"],"evaluacion_id":e["id"],"numero":v["numero"],"fecha":v["creado_en"],"componentes":v["componentes"],"componentes_confirmados":v["componentes_confirmados"],"snapshot":{k:val for k,val in e["snapshot"].items() if k!="clave_huellas"},"limites":LIMITS}

    def comparison(self,c,user,pid,previous,current):
        AccessService.owned(c,user,"practica",pid)
        a,ae,ar=self.historical(c,user,previous)
        b,be,br=self.historical(c,user,current)
        if a["practica_id"]!=pid or b["practica_id"]!=pid:
            raise AccessError(404,"no_encontrado","Recurso no encontrado.")
        return compare(ar,br) | {"desde":self.version(c,user,previous),"hasta":self.version(c,user,current),"transiciones":[{"criterio_codigo":x["criterio_codigo"],"anterior":x["estado"],"actual":y["estado"]} for x,y in zip(ar.results,br.results)],"limites":LIMITS}

    def date_bounds(self,desde,hasta):
        zone=ZoneInfo(self.settings.app_timezone)
        if desde and hasta and desde>hasta:
            raise AccessError(422,"fechas_invalidas","La fecha inicial debe ser anterior a la final.")
        return (datetime.combine(desde,time.min,zone) if desde else None, datetime.combine(hasta+timedelta(days=1),time.min,zone) if hasta else None)

    def history(self,c,user,limit,cursor,desde,hasta,challenge=None):
        start,end=self.date_bounds(desde,hasta)
        anchor=None
        if cursor:
            anchor=AccessService.owned(c,user,"practica",cursor)
        rows=sql(c,'history_practica',uid=user["id"],start=start,end=end,challenge=challenge,anchor=anchor["id"] if anchor else None,time=anchor["actualizado_en"] if anchor else None,limit=limit+1).mappings().all()
        return {"items":[dict(r,cumplimiento=ratio(r["cumplidos"],r["aplicables"]) if r["aplicables"] else None) for r in rows[:limit]],"next_cursor":str(rows[limit-1]["id"]) if len(rows)>limit else None}

    def versions(self,c,user,pid,limit,cursor=None):
        AccessService.owned(c,user,"practica",pid)
        n=0
        if cursor:
            anchor=AccessService.owned(c,user,"version",cursor)
            if anchor["practica_id"]!=pid:
                raise AccessError(404,"no_encontrado","Recurso no encontrado.")
            n=anchor["numero"]
        ids=sql(c,'versions_version_prompt',id=pid,n=n,limit=limit+1).scalars().all()
        return {"items":[self.version(c,user,vid) for vid in ids[:limit]],"next_cursor":str(ids[limit-1]) if len(ids)>limit else None}

    def progress(self,c,user,desde,hasta,limit,cursor=None):
        start,end=self.date_bounds(desde,hasta)
        anchor=None
        if cursor:
            anchor=AccessService.owned(c,user,"version",cursor)
        rows=sql(c,'progress_version_prompt',uid=user["id"],start=start,end=end,cursor=cursor,time=anchor["creado_en"] if anchor else None,limit=limit+1).mappings().all()
        groups=defaultdict(list)
        for r in rows[:limit]:
            groups[(str(r["practica_id"]),r["firma_comparacion"])].append({"id":r["id"],"numero":r["numero"],"fecha":r["creado_en"],"cumplidos":r["cumplidos"],"aplicables":r["aplicables"],"cumplimiento":ratio(r["cumplidos"],r["aplicables"])})
        return {"items":[{"practica_id":pid,"configuracion":sig,"versiones":vs} for (pid,sig),vs in groups.items()],"next_cursor":str(rows[limit-1]["id"]) if len(rows)>limit else None,"limites":LIMITS}
