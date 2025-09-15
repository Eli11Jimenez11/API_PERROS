# api/index.py
import os
import ssl
import asyncpg
import certifi
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

ENV = os.environ.get("ENV", "production")
DATABASE_URL = os.environ.get("DATABASE_URL")

app = FastAPI(title="API de Razas de Perros")

# --- Crear contexto SSL para producción ---
ssl_context_prod = ssl.create_default_context(cafile=certifi.where())

# --- Función para conexión PostgreSQL ---
async def get_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    try:
        ssl_context = ssl_context_prod if ENV == "production" else None
        return await asyncpg.connect(DATABASE_URL, ssl=ssl_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar a la DB: {str(e)}")

# --- Endpoint raíz ---
@app.get("/")
async def root():
    return {"mensaje": "API de Razas de Perros funcionando ✅"}

# --- Listar todas las razas ---
@app.get("/razas")
async def listar_razas():
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT * FROM razas_perros")
        await conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar razas: {str(e)}")

# --- Crear una raza ---
@app.post("/razas")
async def crear_raza(nombre: str, origen: str, tamanio: str, esperanza_vida: int):
    try:
        conn = await get_connection()
        row = await conn.fetchrow(
            """
            INSERT INTO razas_perros (nombre, origen, tamanio, esperanza_vida)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            nombre, origen, tamanio, esperanza_vida
        )
        await conn.close()
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear raza: {str(e)}")

# --- Debug variables ---
@app.get("/debug-env")
async def debug_env():
    return {
        "ENV": ENV,
        "DATABASE_URL_present": bool(DATABASE_URL)
    }
