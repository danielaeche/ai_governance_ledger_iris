import re
import iris

PROHIBIDAS = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
    "merge",
)


def validate_sql(sql):
    s = sql.strip().rstrip(";").strip()
    low = s.lower()
    if not low.startswith("select"):
        raise ValueError("Solo lectura.")
    if ";" in s:
        raise ValueError("Una sola sentencia.")
    if any(re.search(rf"\b{k}\b", low) for k in PROHIBIDAS):
        raise ValueError("Operación no permitida.")
    if "governance.aicalllog" not in low:
        raise ValueError("Solo el registro de auditoría.")
    return s


SCHEMA = """Tabla Governance.AICallLog: CreatedAt, AppName, UserRole, Model, CostUsd,
LatencyMs, PiiFlag (1=tocó datos personales), PiiTypes, RiskFlag (1=riesgo), RiskReason.
Usá DATEADD('month', -1, CURRENT_TIMESTAMP) para 'el último mes'."""


def call_llm(prompt):
    import anthropic

    client = anthropic.Anthropic()  # toma ANTHROPIC_API_KEY del entorno
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def pregunta_a_sql(pregunta):
    prompt = (
        "Sos un asistente que traduce preguntas a SQL para InterSystems IRIS.\n"
        "Devolvé ÚNICAMENTE una consulta SELECT de solo lectura sobre la tabla "
        "Governance.AICallLog. Sin explicaciones, sin punto y coma, sin markdown.\n"
        f"{SCHEMA}\n"
        f"Pregunta: {pregunta}"
    )
    sql = call_llm(prompt).strip()
    sql = re.sub(r"^```sql|^```|```$", "", sql, flags=re.MULTILINE).strip()
    return validate_sql(sql)


# Ejecutar contra IRIS
conn = iris.connect("localhost:1972/USER", "_SYSTEM", "tu_contraseña")
pregunta = "¿Cuántas veces la IA tocó datos personales este mes?"
sql = pregunta_a_sql(pregunta)
cur = conn.cursor()
cur.execute(sql)
print("Pregunta:", pregunta)
print("SQL generado:", sql)
print("Respuesta:", cur.fetchall())
cur.close()
conn.close()
