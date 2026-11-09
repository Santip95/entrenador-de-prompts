"""Motor estructural determinístico. Las configuraciones se reciben como datos."""

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import re
import unicodedata


MOTOR_VERSION = "1.1.0"
NUMERIC_DETECTOR = "secuencia_numerica_7_8_10_v1"
CODES = tuple(f"C{i}" for i in range(1, 7))
TYPES = dict(zip(CODES, (
    "tarea_declarada", "contexto_requerido", "destinatario_declarado",
    "restricciones_declaradas", "formato_declarado", "revision_preventiva",
)))
LIMITATION = "Estos patrones no detectan toda la información sensible"
DETECTORS = {
    "email_v1": ("correo", re.compile(r"(?i)(?<![a-z0-9._%+\-])[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}(?![a-z0-9_\-])"), 0, None, None),
    "telefono_ar_v1": ("telefono", re.compile(r"(?i)(?:\+54[ \t.-]*|(?:tel[eé]fono|tel|celular)[ \t]*[:=]?[ \t]*)(?P<num>[0-9][0-9 \t().-]{6,26}[0-9])"), "num", 8, 13),
    "dni_etiquetado_v1": ("documento", re.compile(r"(?i)\b(?:dni|documento)[ \t]*[:=]?[ \t]*(?P<num>[0-9][0-9. \t-]{5,14}[0-9])\b"), "num", 7, 8),
    NUMERIC_DETECTOR: ("secuencia_numerica", re.compile(r"(?<![0-9])(?:[0-9]{10}|[0-9]{8}|[0-9]{7})(?![0-9])"), 0, None, None),
}


class EvaluationError(ValueError):
    """Error público estable que nunca incluye valores de entrada."""

    def __init__(self, code, *, configuration=False):
        self.code = code
        self.status = 503 if configuration else 422
        super().__init__("Configuración de evaluación inválida." if configuration else
                         "Revisá el formato, las selecciones y los límites de la entrada.")


def _require(condition, code="configuracion_invalida", *, configuration=True):
    if not condition:
        raise EvaluationError(code, configuration=configuration)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _mac(key, value):
    return hmac.new(key, canonical(value).encode("utf-8"), hashlib.sha256).hexdigest()


def normalize(text):
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))


@dataclass(frozen=True)
class EvaluationContext:
    review_key: bytes = field(repr=False)
    fingerprint_key: bytes = field(repr=False)
    subject: str
    practice: str
    key_version: str = "1"

    def __post_init__(self):
        _require(isinstance(self.review_key, bytes) and len(self.review_key) >= 32)
        _require(isinstance(self.fingerprint_key, bytes) and len(self.fingerprint_key) >= 32)
        _require(self.review_key != self.fingerprint_key)
        _require(bool(self.subject) and bool(self.practice) and bool(self.key_version))


@dataclass(frozen=True)
class Confirmation:
    binding: str = field(repr=False)
    keys: frozenset[str] = field(repr=False)


@dataclass(frozen=True)
class Evaluation:
    text: str = field(repr=False)
    components: dict = field(repr=False)
    results: tuple[dict, ...]
    matches: tuple[dict, ...]
    snapshot: dict
    signature: str
    binding: str = field(repr=False)
    fingerprints: tuple[str, ...] = field(repr=False)
    key_version: str
    scope: tuple[str, str] = field(repr=False)
    saveable: bool

    @property
    def fulfilled(self):
        return sum(result["estado"] == "cumple" for result in self.results)

    @property
    def applicable(self):
        return sum(result["estado"] != "no_aplica" for result in self.results)

    def public(self):
        """Texto sólo para su autor; no incluye huellas ni contexto secreto."""
        return deepcopy({
            "motor_version": MOTOR_VERSION, "texto": self.text,
            "resultados": self.results, "coincidencias": self.matches,
            "cumplidos": self.fulfilled, "aplicables": self.applicable,
            "cumplimiento": ratio(self.fulfilled, self.applicable),
            "cumplimiento_mostrado": rounded_ratio(self.fulfilled, self.applicable),
            "limites": [LIMITATION], "guardable": self.saveable,
        })


def confirm(review, keys):
    """Selecciona coincidencias de una revisión; no es un token de autorización."""
    selected = frozenset(keys)
    _require(selected <= {match["clave"] for match in review.matches},
             "confirmacion_invalida", configuration=False)
    return Confirmation(review.binding, selected)


def ratio(numerator, denominator):
    return 100 * numerator / denominator if denominator else None


def rounded_ratio(numerator, denominator):
    value = ratio(numerator, denominator)
    return round(value, 1) if value is not None else None


def _shape(value, keys):
    _require(type(value) is dict and set(value) == set(keys), "entrada_invalida", configuration=False)


def _text(value, maximum=2000):
    _require(type(value) is str, "entrada_invalida", configuration=False)
    result = normalize(value)
    _require(len(result) <= maximum, "limite_excedido", configuration=False)
    return result


def _selection(value, known, *, nullable=True):
    _require((nullable and value is None) or (type(value) is str and value in known),
             "seleccion_desconocida", configuration=False)
    return value


def normalize_objective(value):
    _require(type(value) is str, "entrada_invalida", configuration=False)
    value = normalize(value)
    _require(1 <= len(value.strip()) <= 1000, "objetivo_invalido", configuration=False)
    return value


@dataclass(frozen=True)
class ObjectiveReview:
    objective: str = field(repr=False)
    matches: tuple[dict, ...]
    binding: str = field(repr=False)
    fingerprints: tuple[str, ...] = field(repr=False)


def review_objective(objective, detectors, *, context, confirmation=None):
    """Prevención pura anterior a la práctica; no crea registros ni tokens HTTP."""
    _require(isinstance(context, EvaluationContext))
    objective = normalize_objective(objective)
    _config_list(detectors, DETECTORS)
    binding = _mac(context.review_key, ["inicio", objective, detectors, context.subject, context.practice, context.key_version])
    matches, fingerprints = _scan([("objetivo", objective)], detectors, context, binding)
    selected = frozenset()
    if confirmation is not None:
        _require(isinstance(confirmation, Confirmation) and hmac.compare_digest(confirmation.binding, binding),
                 "revision_desactualizada", configuration=False)
        selected = confirmation.keys
        _require(selected <= {item["clave"] for item in matches}, "confirmacion_invalida", configuration=False)
    return ObjectiveReview(objective, tuple({**m, "confirmada": m["clave"] in selected} for m in matches),
                           binding, fingerprints)


def normalize_draft(draft, catalogs):
    _shape(draft, ("modo", "texto_libre", "componentes_confirmados", "componentes"))
    _require(draft["modo"] in ("guiado", "libre") and type(draft["componentes_confirmados"]) is bool,
             "entrada_invalida", configuration=False)
    c = deepcopy(draft["componentes"])
    _shape(c, ("tarea", "contexto", "destinatario", "restricciones", "formato"))
    shapes = {"tarea": ("texto", "accion_id"), "contexto": ("texto", "campos"),
              "destinatario": ("texto",), "restricciones": ("texto", "selecciones"),
              "formato": ("tipo", "detalle")}
    for key, shape in shapes.items():
        _shape(c[key], shape)
        if "texto" in shape:
            c[key]["texto"] = _text(c[key]["texto"])
    c["formato"]["detalle"] = _text(c["formato"]["detalle"])
    _selection(c["tarea"]["accion_id"], catalogs["acciones"])
    _selection(c["formato"]["tipo"], catalogs["formatos"])
    selected = c["restricciones"]["selecciones"]
    _require(type(selected) is list and len(selected) <= 10 and all(type(x) is str for x in selected),
             "entrada_invalida", configuration=False)
    _require(len(set(selected)) == len(selected), "seleccion_duplicada", configuration=False)
    for value in selected:
        _selection(value, catalogs["restricciones"], nullable=False)
    fields = c["contexto"]["campos"]
    _require(type(fields) is dict and len(fields) <= 10, "entrada_invalida", configuration=False)
    _require(all(key in catalogs["campos_contexto"] for key in fields),
             "seleccion_desconocida", configuration=False)
    c["contexto"]["campos"] = {key: _text(value) for key, value in fields.items()}
    _require(len(canonical(c)) <= 20000, "limite_excedido", configuration=False)
    free = _text(draft["texto_libre"], 10000)
    if draft["modo"] == "libre":
        _require(draft["componentes_confirmados"], "componentes_sin_confirmar", configuration=False)
    else:
        _require(not free, "texto_guiado_contradictorio", configuration=False)
    return {**draft, "componentes": c, "texto_libre": free}


def validate_configuration(configuration, rules, catalogs, criteria):
    _require(type(configuration) is dict and set(configuration) == set(CODES))
    _require(type(criteria) is dict and set(criteria) == set(CODES))
    _require(type(catalogs) is dict)
    for group in ("acciones", "formatos", "restricciones", "campos_contexto"):
        _require(type(catalogs.get(group)) is dict and all(
            type(k) is str and type(v) is str for k, v in catalogs[group].items()))
    _require(type(rules) is list)
    active = {}
    for rule in rules:
        _require(type(rule) is dict and rule.get("criterio_codigo") in CODES)
        code = rule["criterio_codigo"]
        _require(type(rule.get("activa")) is bool)
        if not rule["activa"]:
            continue
        _require(code not in active and rule.get("tipo") == TYPES[code])
        _require(type(rule.get("version")) is int and rule["version"] >= 1)
        _require(isinstance(rule.get("id", rule.get("codigo")), str))
        parameters = rule.get("parametros")
        _require(type(parameters) is dict)
        if code == "C6":
            _require(set(parameters) == {"detectores_activos"})
            _config_list(parameters["detectores_activos"], DETECTORS)
        else:
            _require(parameters == {"combinacion": "AND"})
        messages = rule.get("mensajes")
        _require(type(messages) is dict and all(type(messages.get(key)) is str for key in
                 ("cumple", "pendiente", "accion", "no_aplica")))
        if code == "C6":
            _require(type(messages.get("confirmada")) is str)
        active[code] = rule
    allowed = {"C1": {"acciones_permitidas"}, "C2": {"campos_requeridos", "exigir_texto"},
               "C3": set(), "C4": {"selecciones_requeridas", "exigir_texto"},
               "C5": {"tipos_permitidos", "exigir_detalle"}, "C6": {"detectores_activos"}}
    effective = {}
    for code in CODES:
        item = configuration[code]
        _require(type(item) is dict and set(item) == {"aplica", "obligatorio", "parametros"})
        _require(type(item["aplica"]) is bool and type(item["obligatorio"]) is bool)
        _require(item["aplica"] == item["obligatorio"])
        _require(code not in ("C1", "C5", "C6") or item["aplica"])
        _require(type(item["parametros"]) is dict and set(item["parametros"]) <= allowed[code])
        _require(type(criteria[code]) is dict and all(type(criteria[code].get(key)) is str
                                                   for key in ("nombre", "descripcion")))
        if item["aplica"]:
            _require(code in active, "regla_activa_faltante")
        parameters = {**(active.get(code, {}).get("parametros", {})), **item["parametros"]}
        if code == "C1":
            _config_list(parameters.get("acciones_permitidas"), catalogs["acciones"], nonempty=True)
        if code == "C2":
            _config_list(parameters.get("campos_requeridos"), catalogs["campos_contexto"])
            _require(type(parameters.get("exigir_texto")) is bool)
            _require(not item["aplica"] or parameters["campos_requeridos"] or parameters["exigir_texto"])
        if code == "C4":
            _config_list(parameters.get("selecciones_requeridas"), catalogs["restricciones"])
            _require(type(parameters.get("exigir_texto")) is bool)
            _require(not item["aplica"] or parameters["selecciones_requeridas"] or parameters["exigir_texto"])
        if code == "C5":
            _config_list(parameters.get("tipos_permitidos"), catalogs["formatos"], nonempty=True)
            _require(type(parameters.get("exigir_detalle")) is bool)
        if code == "C6":
            _config_list(parameters.get("detectores_activos"), DETECTORS)
        effective[code] = parameters
    return active, effective


def _config_list(value, known, *, nonempty=False):
    _require(type(value) is list and len(value) <= 10 and all(type(x) is str and x in known for x in value))
    _require(len(value) == len(set(value)) and (not nonempty or len(value) > 0))


def assemble(components, catalogs):
    sections = []
    for code, key in enumerate(("tarea", "contexto", "destinatario", "restricciones", "formato"), 1):
        component = components[key]
        lines = [component.get("texto", "")]
        if key == "tarea" and component["accion_id"]:
            lines.append("Acción: " + catalogs["acciones"][component["accion_id"]])
        if key == "contexto":
            lines.extend(catalogs["campos_contexto"][k] + ": " + v
                         for k, v in sorted(component["campos"].items()) if v.strip())
        if key == "restricciones":
            lines.extend(catalogs["restricciones"][k] for k in component["selecciones"])
        if key == "formato":
            if component["tipo"]:
                lines.append(catalogs["formatos"][component["tipo"]])
            lines.append(component["detalle"])
        lines = [line for line in lines if line.strip()]
        if lines:
            title = ("Tarea", "Contexto", "Destinatario", "Restricciones", "Formato")[code - 1]
            sections.append(title + ":\n" + "\n".join(lines))
    return "\n\n".join(sections)


def _scan(values, detectors, context, binding):
    matches, fingerprints, seen = [], [], set()
    for path, text in values:
        # Prioridad de las alertas anteriores independiente del orden configurado.
        # Los spans son internos y nunca se devuelven ni se persisten.
        covered = []
        ordered = [d for d in detectors if d != NUMERIC_DETECTOR]
        if NUMERIC_DETECTOR in detectors:
            ordered.append(NUMERIC_DETECTOR)
        for detector in ordered:
            kind, expression, group, minimum, maximum = DETECTORS[detector]
            for match in expression.finditer(text):
                value = match.group(group)
                if minimum is not None and not minimum <= sum(c in "0123456789" for c in value) <= maximum:
                    continue
                if detector == NUMERIC_DETECTOR and any(start <= match.start() and match.end() <= end for start, end in covered):
                    continue
                if detector != NUMERIC_DETECTOR:
                    covered.append((match.start(), match.end()))
                identity = (kind, path, match.start(), match.end())
                if identity in seen:
                    continue
                seen.add(identity)
                key = _mac(context.review_key, [binding, *identity])
                matches.append({"clave": key, "tipo": kind, "campo": path,
                                "mensaje": ("Secuencia de 7, 8 o 10 dígitos; podría contener información sensible. Revisala antes de guardar."
                                            if detector == NUMERIC_DETECTOR else
                                            "Posible dato sensible; revisá esta coincidencia.")})
                fingerprints.append(_mac(context.fingerprint_key, [context.practice, kind, path, value]))
    return tuple(matches), tuple(fingerprints)


def _texts(draft, objective):
    if objective is not None:
        yield "objetivo", objective
    c = draft["componentes"]
    for key in ("tarea", "contexto", "destinatario", "restricciones"):
        yield f"componentes.{key}.texto", c[key]["texto"]
    for key, value in sorted(c["contexto"]["campos"].items()):
        yield f"componentes.contexto.campos.{key}", value
    yield "componentes.formato.detalle", c["formato"]["detalle"]
    if draft["modo"] == "libre":
        yield "texto_libre", draft["texto_libre"]


def _condition(code, parameters, catalogs):
    if code == "C1":
        return "Declarar la tarea y elegir una acción admitida: " + ", ".join(
            catalogs["acciones"][key] for key in parameters["acciones_permitidas"]) + "."
    if code == "C2":
        labels = [catalogs["campos_contexto"][key] for key in parameters["campos_requeridos"]]
        return ("Completar contexto: " + ", ".join(labels) + ". " if labels else "") + (
            "Declarar el texto de contexto." if parameters["exigir_texto"] else "Completar los campos indicados.")
    if code == "C3":
        return "Declarar el destinatario."
    if code == "C4":
        labels = [catalogs["restricciones"][key] for key in parameters["selecciones_requeridas"]]
        return ("Seleccionar las condiciones: " + "; ".join(labels) + ". " if labels else "") + (
            "Declarar el texto de restricciones." if parameters["exigir_texto"] else "Completar las selecciones indicadas.")
    if code == "C5":
        return "Elegir un formato admitido: " + ", ".join(catalogs["formatos"][key]
            for key in parameters["tipos_permitidos"]) + (" y declarar su detalle." if parameters["exigir_detalle"] else ".")
    return "Sin coincidencias de los patrones configurados o con cada coincidencia revisada y confirmada."


def _evidence(code, components, matches, missing):
    evidence = {"faltantes": list(missing)}
    if code == "C1":
        evidence.update(texto_presente=bool(components["tarea"]["texto"].strip()), accion_id=components["tarea"]["accion_id"])
    if code == "C2":
        evidence.update(texto_presente=bool(components["contexto"]["texto"].strip()),
                        campos_presentes=sorted(k for k, v in components["contexto"]["campos"].items() if v.strip()))
    if code == "C3": evidence["texto_presente"] = bool(components["destinatario"]["texto"].strip())
    if code == "C4": evidence["selecciones"] = list(components["restricciones"]["selecciones"])
    if code == "C5": evidence.update(tipo=components["formato"]["tipo"], detalle_presente=bool(components["formato"]["detalle"].strip()))
    if code == "C6": evidence.update(coincidencias=len(matches), confirmadas=sum(m["confirmada"] for m in matches))
    return evidence


def evaluate(draft, configuration, rules, catalogs, criteria, *, context, objective=None, confirmation=None):
    _require(isinstance(context, EvaluationContext))
    active, effective = validate_configuration(configuration, rules, catalogs, criteria)
    draft = normalize_draft(draft, catalogs)
    if objective is not None:
        objective = normalize_objective(objective)
    c = draft["componentes"]
    text = draft["texto_libre"] if draft["modo"] == "libre" else assemble(c, catalogs)
    _require(len(text) <= 10000, "limite_excedido", configuration=False)
    snapshot = {"motor_version": MOTOR_VERSION, "configuracion": deepcopy(configuration),
                "reglas": deepcopy(active), "criterios": deepcopy(criteria),
                "parametros_efectivos": deepcopy(effective), "catalogos": deepcopy(catalogs)}
    signature = _digest([MOTOR_VERSION, {code: {
        "aplica": configuration[code]["aplica"], "parametros": effective[code],
        "regla_id": active.get(code, {}).get("id", active.get(code, {}).get("codigo")),
        "version": active.get(code, {}).get("version"), "tipo": active.get(code, {}).get("tipo"),
    } for code in CODES}])
    binding = _mac(context.review_key, [draft, objective, snapshot, context.subject, context.practice, context.key_version])
    matches, fingerprints = _scan(_texts(draft, objective), effective["C6"]["detectores_activos"], context, binding)
    confirmed = frozenset()
    if confirmation is not None:
        _require(isinstance(confirmation, Confirmation) and hmac.compare_digest(confirmation.binding, binding),
                 "revision_desactualizada", configuration=False)
        confirmed = confirmation.keys
        _require(confirmed <= {item["clave"] for item in matches}, "confirmacion_invalida", configuration=False)
    matches = tuple({**item, "confirmada": item["clave"] in confirmed} for item in matches)
    results = []
    for code in CODES:
        rule = active.get(code)
        p = effective[code]
        missing = []
        applies = configuration[code]["aplica"]
        if applies:
            if code == "C1":
                if not c["tarea"]["texto"].strip(): missing.append("componentes.tarea.texto")
                if c["tarea"]["accion_id"] not in p["acciones_permitidas"]: missing.append("componentes.tarea.accion_id")
            if code == "C2":
                missing.extend("componentes.contexto.campos." + k for k in p["campos_requeridos"]
                               if not c["contexto"]["campos"].get(k, "").strip())
                if p["exigir_texto"] and not c["contexto"]["texto"].strip(): missing.append("componentes.contexto.texto")
            if code == "C3" and not c["destinatario"]["texto"].strip(): missing.append("componentes.destinatario.texto")
            if code == "C4":
                missing.extend("componentes.restricciones.selecciones." + k for k in p["selecciones_requeridas"]
                               if k not in c["restricciones"]["selecciones"])
                if p["exigir_texto"] and not c["restricciones"]["texto"].strip(): missing.append("componentes.restricciones.texto")
            if code == "C5":
                if c["formato"]["tipo"] not in p["tipos_permitidos"]: missing.append("componentes.formato.tipo")
                if p["exigir_detalle"] and not c["formato"]["detalle"].strip(): missing.append("componentes.formato.detalle")
            if code == "C6" and any(not item["confirmada"] for item in matches): missing.append("coincidencias_sin_confirmar")
        state = "no_aplica" if not applies else ("advertencia" if code == "C6" else "revisar") if missing else "cumple"
        messages = rule["mensajes"] if rule else {}
        message_key = "no_aplica" if not applies else "pendiente" if missing else (
            "confirmada" if code == "C6" and matches else "cumple")
        results.append({
            "criterio_codigo": code, "nombre": criteria[code]["nombre"], "estado": state,
            "regla_id": (rule.get("id", rule.get("codigo")) if applies else None),
            "regla_version": (rule["version"] if applies else None),
            "condicion_esperada": _condition(code, p, catalogs) if applies else "No aplica según la configuración.",
            "evidencia": _evidence(code, c, matches, missing) if applies else {"aplica": False},
            "mensaje": messages.get(message_key, "Este criterio no corresponde a la configuración de esta práctica."),
            "accion_sugerida": messages["accion"] if missing else "",
        })
    saveable = bool(text.strip()) and not any(not item["confirmada"] for item in matches)
    return Evaluation(text, deepcopy(c), tuple(results), matches, snapshot, signature, binding,
                      fingerprints, context.key_version, (context.subject, context.practice), saveable)


def compare(previous, current):
    """Indicadores puros; no implementa el endpoint ni persiste versiones."""
    same = previous.signature == current.signature and previous.scope == current.scope
    alerts_comparable = previous.key_version == current.key_version and previous.scope == current.scope
    new_alerts = sum((Counter(current.fingerprints) - Counter(previous.fingerprints)).values()) if alerts_comparable else None
    delta = ratio(current.fulfilled, current.applicable) - ratio(previous.fulfilled, previous.applicable) if same else None
    observations = [r["criterio_codigo"] for r in previous.results if r["estado"] in ("revisar", "advertencia")]
    solved = sum(r["criterio_codigo"] in observations and r["estado"] == "cumple" for r in current.results)
    return {"comparable": same, "razon": None if same else "Cambiaron las reglas, la configuración o la práctica.",
            "delta_pp": delta, "resolucion": ratio(solved, len(observations)) if same else None,
            "alertas_nuevas": new_alerts,
            "aviso_alertas": None if alerts_comparable else "No se pudo determinar si hay alertas nuevas",
            "mejora_estructural": bool(same and delta is not None and delta > 0 and new_alerts == 0)}


def transfer(first_baseline, first_new):
    if first_baseline.signature != first_new.signature:
        return None
    return ratio(first_new.fulfilled, first_new.applicable) - ratio(first_baseline.fulfilled, first_baseline.applicable)


def comprehension(correct, consulted):
    """Recibe conteos de evaluación humana; no califica texto."""
    _require(type(correct) is int and type(consulted) is int and 0 <= correct <= consulted,
             "conteo_invalido", configuration=False)
    return ratio(correct, consulted)
