"""Persistencia de Kevin: SQLite local y PostgreSQL externo, sin borrar datos."""
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')  # No buscar configuraciones en proyectos vecinos.


def normalizar_url(url: str) -> str:
    if url.startswith('postgres://'):
        return 'postgresql+psycopg://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        return 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


class Base(DeclarativeBase):
    pass


class ModeloGuardado(Base):
    __tablename__ = 'modelos'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(String(120), index=True)
    sentido: Mapped[str] = mapped_column(String(3), index=True)
    estado: Mapped[str] = mapped_column(String(30), index=True)
    modelo: Mapped[dict] = mapped_column(JSON)
    resultado: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def conectar(url: str | None = None):
    fallback = 'sqlite:///' + (ROOT / 'simplex_lab.db').as_posix()
    url = normalizar_url(url or os.getenv('DATABASE_URL') or fallback)
    if os.getenv('RENDER') and not url.startswith('postgresql+psycopg://'):
        raise RuntimeError('Render requiere PostgreSQL externo: configure DATABASE_URL de Neon.')
    engine = create_engine(
        url, pool_pre_ping=True,
        connect_args={'check_same_thread': False} if url.startswith('sqlite:') else {},
    )
    return engine, sessionmaker(engine)


def inicializar(engine):
    """Crear tablas ausentes; no eliminar tablas ni registros existentes."""
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    engine, _ = conectar()
    try:
        inicializar(engine)
        print('Esquema inicializado sin eliminar datos.')
    finally:
        engine.dispose()
