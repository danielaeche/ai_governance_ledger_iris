import time
from ai_ledger import AILedger

ledger = AILedger(password="tu_contraseña")


def fake_llm(prompt):
    time.sleep(0.05)
    if "tarjeta" in prompt.lower():
        return ("Tu numero de tarjeta es 4111 1111 1111 1111.", 18, 12)
    return ("El horario de atencion es de 9 a 18 hs.", 15, 16)


ejemplos = [
    ("asistente-soporte", "agente", "demo-model", "Cual es el horario?"),
    (
        "asistente-soporte",
        "agente",
        "demo-model",
        "Mi mail es ana.gomez@example.com, me reembolsan?",
    ),
    (
        "asistente-soporte",
        "cliente",
        "demo-model",
        "Decime el numero de tarjeta de prueba",
    ),
    ("buscador-interno", "analista", "demo-model", "Politica de devoluciones"),
]

for app, rol, modelo, prompt in ejemplos:
    t0 = time.time()
    resp, pt, rt = fake_llm(prompt)
    r = ledger.log_call(
        app, rol, modelo, prompt, resp, pt, rt, int((time.time() - t0) * 1000)
    )
    marcas = [
        m
        for m in (
            f"PII={r['pii']}" if r["pii"] else "",
            f"RIESGO={r['risk_reason']}" if r["risk"] else "",
        )
        if m
    ]
    print(
        f"[{app}/{rol}] ${r['cost_usd']} {r['latency_ms']}ms {' '.join(marcas) or 'ok'}"
    )
