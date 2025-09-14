import os
import ssl
from fastapi import FastAPI, HTTPException
import asyncpg
import certifi
from dotenv import load_dotenv

app = FastAPI(title="API de Razas de Perros")

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

# 🔹 SSL para producción
ssl_context_prod = ssl.create_default_context(cafile=certifi.where())

# 🔹 SSL para desarrollo (ignora verificación, solo local/dev)
ssl_context_dev = ssl.create_default_context()
ssl_context_dev.check_hostname = False
ssl_context_dev.verify_mode = ssl.CERT_NONE

# 🔹 Detecta si estamos en producción o local
ENV = os.environ.get("ENV", "development")  # por ejemplo ENV=production en Vercel

async def get_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    
    ssl_context = ssl_context_prod if ENV == "production" else ssl_context_dev

    try:
        return await asyncpg.connect(DATABASE_URL, ssl=ssl_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar a la DB: {str(e)}")

@app.get("/")
async def root():
    return {"mensaje": "API de Razas de Perros funcionando ✅"}

@app.get("/razas")
async def listar_razas():
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT * FROM razas_perros")
        await conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Error al listar razas: {str(e)}")

@app.post("/razas")
async def crear_raza(nombre: str, origen: str, tamanio: str, esperanza_vida: int):
    try:
        conn = await get_connection()
        row = await conn.fetchrow("""
            INSERT INTO razas_perros (nombre, origen, tamanio, esperanza_vida)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, nombre, origen, tamanio, esperanza_vida)
        await conn.close()
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear raza: {str(e)}")

@app.get("/debug-env")
async def debug_env():
    return {
        "DATABASE_URL_present": bool(DATABASE_URL),
        "DATABASE_URL_truncated": (DATABASE_URL[:20] + "...") if DATABASE_URL else None,
        "ENV": ENV
    }
