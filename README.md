# AI Governance Ledger sobre InterSystems IRIS

> Código del tutorial publicado en la Comunidad de Desarrolladores de InterSystems.

Un **registro auditable de llamadas a modelos de IA (LLMs)** construido sobre InterSystems IRIS.
Cada llamada queda anotada —quién, qué modelo, qué entró, qué salió, cuánto costó, si tocó
datos personales (PII) y si la respuesta fue de riesgo— y el registro se puede consultar de
tres formas: un tablero en SQL, un agente que responde en lenguaje natural, y una búsqueda
semántica de incidentes con IRIS Vector Search.

Es una prueba de concepto reproducible: la pieza técnica de trazabilidad sobre la que se apoyan
marcos de gobernanza de IA como la ISO/IEC 42001 o la Ley de IA de la UE.

## Requisitos

- Docker
- Python 3.8 o superior

## Puesta en marcha

**1. Levantar IRIS Community en Docker**

```bash
docker compose up -d
```

IRIS tarda 30-60 segundos en inicializar. Portal de gestión: `http://localhost:52773/csp/sys/UtilHome.csp`

**2. Fijar la contraseña**

En el primer ingreso al portal (usuario `_SYSTEM`), IRIS obliga a cambiar la contraseña.
Elegí una y usá esa misma en los scripts (reemplazá el placeholder `tu_contraseña`).

**3. Instalar el driver y crear la tabla**

```bash
python3 -m pip install intersystems-irispython
python3 create_table.py
```

**4. Registrar llamadas de ejemplo**

```bash
python3 demo.py
```

Simula cuatro llamadas (una con PII, una de riesgo) y las registra en IRIS.

**5. Consultar el registro**

- **Tablero SQL:** ejecutá las consultas de `governance_queries.sql` en System Explorer → SQL del portal.
- **Agente en lenguaje natural** (requiere una API key de un LLM):

```bash
  python3 -m pip install anthropic
  export ANTHROPIC_API_KEY=...
  python3 audit_agent.py
```

- **Búsqueda semántica de incidentes** (IRIS Vector Search):

```bash
  python3 -m pip install sentence-transformers
  python3 incident_search.py
```

## Archivos

- `docker-compose.yml` — IRIS Community local.
- `create_table.py` — crea la tabla `Governance.AICallLog` con el driver de Python.
- `ai_ledger.py` — el _wrapper_ que registra en IRIS + los chequeos de PII, riesgo y costo.
- `demo.py` — cuatro llamadas simuladas que se registran.
- `governance_queries.sql` — el tablero de auditoría (consultas SQL).
- `audit_agent.py` — agente text-to-SQL: preguntas en lenguaje natural, con guardrail de solo lectura.
- `incident_search.py` — búsqueda semántica de incidentes con Vector Search.

## Notas honestas

- Los detectores de PII y de riesgo son un **punto de partida**, no una solución de producción.
  En serio se reemplazan por un detector robusto (p. ej. Presidio) y un evaluador de respuestas.
  Lo que vale es la arquitectura: interceptar y registrar en IRIS.
- El validador del agente es una **primera barrera**; en producción se refuerza con una vista de
  solo lectura o un usuario con permisos exclusivos de `SELECT` sobre la tabla de auditoría.
- No pongas datos reales de clientes, activos internos ni contraseñas reales: el ejemplo es un
  juguete genérico a propósito.
