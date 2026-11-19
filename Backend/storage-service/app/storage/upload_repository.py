
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv(
    "UPLOADS_DB_PATH",
    "/app/data/uploads.db"
)


def conectar():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(DB_PATH, timeout=10)
    conexion.row_factory = sqlite3.Row

    return conexion



def inicializar_db():
    with conectar() as conexion:
        conexion.execute("PRAGMA journal_mode=WAL")

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                task_id TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                content_type TEXT NOT NULL,
                size INTEGER NOT NULL,
                status TEXT NOT NULL,
                url TEXT,
                error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def crear_upload(
    task_id,
    usuario_id,
    file_name,
    content_type,
    size
):
    with conectar() as conexion:
        conexion.execute("""
            INSERT INTO uploads (
                task_id,
                usuario_id,
                file_name,
                content_type,
                size,
                status
            )
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            task_id,
            usuario_id,
            file_name,
            content_type,
            size
        ))


def actualizar_upload(
    task_id,
    status,
    url=None,
    error=None
):
    with conectar() as conexion:
        conexion.execute("""
            UPDATE uploads
            SET status = ?,
                url = ?,
                error = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE task_id = ?
        """, (
            status,
            url,
            error,
            task_id
        ))


def obtener_upload(task_id, usuario_id):
    with conectar() as conexion:
        resultado = conexion.execute("""
            SELECT *
            FROM uploads
            WHERE task_id = ?
              AND usuario_id = ?
        """, (
            task_id,
            usuario_id
        )).fetchone()

    return dict(resultado) if resultado else None
