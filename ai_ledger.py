import re

# --- Señales de gobernanza (funciones simples, solo para ilustrar) ---
PII_PATTERNS = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b",
    "tarjeta": r"\b(?:\d[ -]?){13,16}\b",
    "dni_nie": r"\b[XYZ]?\d{7,8}[A-Z]\b",
    "telefono": r"(?:\+\d{1,3}[ -]?)?(?:\d[ -]?){9,}",
}


def detect_pii(texto):
    return [t for t, p in PII_PATTERNS.items() if texto and re.search(p, texto)]


def check_risk(respuesta):
    if not respuesta or not respuesta.strip():
        return True, "respuesta_vacia"
    if "numero de tarjeta" in respuesta.lower():
        return True, "posible_filtracion:numero de tarjeta"
    return False, None


# --- Costo estimado por modelo (USD por 1000 tokens) ---
PRICE_TABLE = {
    "demo-model": {"in": 0.0005, "out": 0.0015},
    "claude-sonnet": {"in": 0.003, "out": 0.015},
    "gpt-generic": {"in": 0.0005, "out": 0.0015},
}


def estimate_cost(model, prompt_tokens, response_tokens):
    if model not in PRICE_TABLE:
        # Ojo: si el modelo no está en la tabla, el costo da 0.
        # En un caso real conviene avisar, no registrar "gratis" en silencio.
        print(f"[aviso] modelo '{model}' sin precio definido; costo = 0")
    p = PRICE_TABLE.get(model, {"in": 0.0, "out": 0.0})
    return round((prompt_tokens/1000.0)*p["in"] + (response_tokens/1000.0)*p["out"], 6)


# --- El wrapper que conecta a IRIS y registra ---
class AILedger:
    def __init__(
        self,
        host="localhost",
        port=1972,
        namespace="USER",
        user="_SYSTEM",
        password="tu_contraseña",
    ):
        import iris

        conn_str = f"{host}:{port}/{namespace}"
        self.conn = iris.connect(conn_str, user, password)

    def log_call(
        self,
        app,
        role,
        model,
        prompt,
        response,
        prompt_tokens,
        response_tokens,
        latency_ms,
    ):
        pii_types = detect_pii(f"{prompt}\n{response}")
        risk_flag, risk_reason = check_risk(response)
        cost = estimate_cost(model, prompt_tokens, response_tokens)
        sql = """INSERT INTO Governance.AICallLog
                 (AppName, UserRole, Model, Prompt, Response, PromptTokens,
                  ResponseTokens, CostUsd, LatencyMs, PiiFlag, PiiTypes, RiskFlag, RiskReason)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"""
        cur = self.conn.cursor()
        cur.execute(
            sql,
            [
                app,
                role,
                model,
                prompt,
                response,
                prompt_tokens,
                response_tokens,
                cost,
                latency_ms,
                1 if pii_types else 0,
                ",".join(pii_types) if pii_types else None,
                1 if risk_flag else 0,
                risk_reason,
            ],
        )
        self.conn.commit()
        cur.close()
        return {
            "app": app,
            "role": role,
            "model": model,
            "cost_usd": cost,
            "latency_ms": latency_ms,
            "pii": pii_types,
            "risk": risk_flag,
            "risk_reason": risk_reason,
        }
