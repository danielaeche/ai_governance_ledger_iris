-- 1) Volumen y costo por modelo (este mes)
SELECT Model, COUNT(*) AS Llamadas, SUM(CostUsd) AS CostoUsd, AVG(LatencyMs) AS LatenciaMediaMs
FROM Governance.AICallLog
WHERE CreatedAt >= DATEADD('month', -1, CURRENT_TIMESTAMP)
GROUP BY Model ORDER BY CostoUsd DESC;

-- 2) Cuántas llamadas tocaron PII, y de qué tipo
SELECT PiiTypes, COUNT(*) AS Cantidad
FROM Governance.AICallLog WHERE PiiFlag = 1
GROUP BY PiiTypes ORDER BY Cantidad DESC;

-- 3) Respuestas marcadas de riesgo, con el motivo
SELECT RiskReason, COUNT(*) AS Cantidad
FROM Governance.AICallLog WHERE RiskFlag = 1
GROUP BY RiskReason ORDER BY Cantidad DESC;

-- 4) Actividad por producto y rol (quién usa IA y para qué)
SELECT AppName, UserRole, COUNT(*) AS Llamadas
FROM Governance.AICallLog
GROUP BY AppName, UserRole ORDER BY Llamadas DESC;

-- 5) Últimas 10 interacciones de alto riesgo
SELECT TOP 10 CAST(CreatedAt AS VARCHAR(30)) AS Fecha,
       AppName, Model, RiskReason, PiiTypes
FROM Governance.AICallLog
WHERE RiskFlag = 1 OR PiiFlag = 1
ORDER BY CreatedAt DESC;