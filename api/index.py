# api/index.py
import os
import ssl
import asyncpg
import certifi
import httpx
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

ENV = os.environ.get("ENV", "production")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

app = FastAPI(title="API de Razas de Perros")

ssl_context_prod = ssl.create_default_context(cafile=certifi.where())

# --- Función para conexión TCP (solo local) ---
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

# --- Listar razas ---
@app.get("/razas")
async def listar_razas():
    if ENV == "production":
        # Usar Supabase Data API
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise HTTPException(status_code=500, detail="Variables SUPABASE_URL o SUPABASE_KEY no configuradas")
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/razas_perros?select=*", headers=headers)
            if res.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error al listar razas: {res.text}")
            return res.json()
    else:
        # Conexión directa TCP (local)
        try:
            conn = await get_connection()
            rows = await conn.fetch("SELECT * FROM razas_perros")
            await conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar razas: {str(e)}")

# --- Crear raza (solo local, TCP) ---
@app.post("/razas")
async def crear_raza(nombre: str, origen: str, tamanio: str, esperanza_vida: int):
    if ENV == "production":
        raise HTTPException(status_code=400, detail="Creación de razas no soportada en producción vía TCP. Usa Supabase Studio o Data API.")
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
        "DATABASE_URL_present": bool(DATABASE_URL),
        "SUPABASE_URL_present": bool(SUPABASE_URL),
        "SUPABASE_KEY_present": bool(SUPABASE_KEY)
    }
