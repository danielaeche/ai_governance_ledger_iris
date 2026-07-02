import iris

conn = iris.connect("localhost:1972/USER", "_SYSTEM", "tu_contraseña")
cur = conn.cursor()
cur.execute("""
CREATE TABLE Governance.AICallLog (
    LogId           BIGINT IDENTITY,
    CreatedAt       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    AppName         VARCHAR(100),
    UserRole        VARCHAR(50),
    Model           VARCHAR(100),
    Prompt          VARCHAR(10000),
    Response        VARCHAR(10000),
    PromptTokens    INTEGER,
    ResponseTokens  INTEGER,
    CostUsd         NUMERIC(12,6),
    LatencyMs       INTEGER,
    PiiFlag         BIT,
    PiiTypes        VARCHAR(255),
    RiskFlag        BIT,
    RiskReason      VARCHAR(255)
)
""")
conn.commit()
cur.close()
conn.close()
print("Tabla Governance.AICallLog creada.")
