-- Equivalente PostgreSQL del esquema SQLAlchemy; no elimina datos.
CREATE TABLE IF NOT EXISTS modelos (
 id VARCHAR(36) PRIMARY KEY,
 nombre VARCHAR(120) NOT NULL,
 sentido VARCHAR(3) NOT NULL,
 estado VARCHAR(30) NOT NULL,
 modelo JSON NOT NULL,
 resultado JSON NULL,
 creado TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_modelos_nombre ON modelos(nombre);
CREATE INDEX IF NOT EXISTS ix_modelos_sentido ON modelos(sentido);
CREATE INDEX IF NOT EXISTS ix_modelos_estado ON modelos(estado);
