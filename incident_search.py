import iris
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
DIM = 384


def embed(texto):
    vec = MODEL.encode(texto or "", normalize_embeddings=True).tolist()
    return ",".join(str(x) for x in vec)


conn = iris.connect("localhost:1972/USER", "_SYSTEM", "tu_contraseña")
cur = conn.cursor()

# Backfill: calcular el vector de cada fila que aún no lo tenga
cur.execute(
    "SELECT LogId, Prompt, Response FROM Governance.AICallLog WHERE Embedding IS NULL"
)
for log_id, prompt, response in cur.fetchall():
    cur.execute(
        "UPDATE Governance.AICallLog SET Embedding = TO_VECTOR(?, double, 384) WHERE LogId = ?",
        [embed(f"{prompt} {response}"), log_id],
    )
conn.commit()
print("Embeddings calculados.")


# Búsqueda por significado
def incidentes_parecidos(descripcion, k=5):
    q = embed(descripcion)
    cur.execute(
        """SELECT TOP ? AppName, Model, RiskReason, PiiTypes,
                          VECTOR_COSINE(Embedding, TO_VECTOR(?, double, 384)) AS Similitud
                   FROM Governance.AICallLog
                   WHERE Embedding IS NOT NULL
                   ORDER BY Similitud DESC""",
        [k, q],
    )
    return cur.fetchall()


print("\nIncidentes parecidos a: 'un usuario compartió el número de su tarjeta'")
for fila in incidentes_parecidos("un usuario compartió el número de su tarjeta"):
    print(fila)

cur.close()
conn.close()
