# api/index.py
import os
import ssl
import certifi
import asyncpg
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

ENV = os.environ.get("ENV", "production")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

app = FastAPI(title="API de Razas de Perros")

ssl_context_prod = ssl.create_default_context(cafile=certifi.where())

# --- Modelo Pydantic para validación ---
class Raza(BaseModel):
    nombre: str
    origen: str
    tamanio: str
    esperanza_vida: int

# --- Conexión directa PostgreSQL (solo local) ---
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
        # PRODUCCIÓN: Supabase REST API
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise HTTPException(status_code=500, detail="SUPABASE_URL o SUPABASE_KEY no configuradas")
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                res = await client.get(f"{SUPABASE_URL}/rest/v1/razas_perros?select=*", headers=headers)
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Error de conexión a Supabase: {str(e)}")
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Error al listar razas: {res.text}")
            return res.json()
    else:
        # LOCAL: PostgreSQL directo
        try:
            conn = await get_connection()
            rows = await conn.fetch("SELECT * FROM razas_perros")
            await conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar razas: {str(e)}")

# --- Crear raza ---
@app.post("/razas")
async def crear_raza(raza: Raza):
    if ENV == "production":
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(f"{SUPABASE_URL}/rest/v1/razas_perros", headers=headers, json=raza.dict())
            if res.status_code not in [200, 201]:
                raise HTTPException(status_code=res.status_code, detail=f"Error al crear raza: {res.text}")
            return res.json()
    else:
        try:
            conn = await get_connection()
            row = await conn.fetchrow(
                "INSERT INTO razas_perros (nombre, origen, tamanio, esperanza_vida) VALUES ($1, $2, $3, $4) RETURNING *",
                raza.nombre, raza.origen, raza.tamanio, raza.esperanza_vida
            )
            await conn.close()
            return dict(row)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al crear raza: {str(e)}")

# --- Actualizar raza ---
@app.patch("/razas/{id}")
async def actualizar_raza(id: int, raza: Raza):
    if ENV == "production":
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.patch(f"{SUPABASE_URL}/rest/v1/razas_perros?id=eq.{id}", headers=headers, json=raza.dict())
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Error al actualizar raza: {res.text}")
            return res.json()
    else:
        try:
            conn = await get_connection()
            row = await conn.fetchrow(
                "UPDATE razas_perros SET nombre=$1, origen=$2, tamanio=$3, esperanza_vida=$4 WHERE id=$5 RETURNING *",
                raza.nombre, raza.origen, raza.tamanio, raza.esperanza_vida, id
            )
            await conn.close()
            if row:
                return dict(row)
            raise HTTPException(status_code=404, detail="Raza no encontrada")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar raza: {str(e)}")

# --- Eliminar raza ---
@app.delete("/razas/{id}")
async def eliminar_raza(id: int):
    if ENV == "production":
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.delete(f"{SUPABASE_URL}/rest/v1/razas_perros?id=eq.{id}", headers=headers)
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Error al eliminar raza: {res.text}")
            return {"mensaje": f"Raza con id {id} eliminada correctamente"}
    else:
        try:
            conn = await get_connection()
            result = await conn.execute("DELETE FROM razas_perros WHERE id=$1", id)
            await conn.close()
            if result[-1] == "0":
                raise HTTPException(status_code=404, detail="Raza no encontrada")
            return {"mensaje": f"Raza con id {id} eliminada correctamente"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al eliminar raza: {str(e)}")

# --- Debug de variables de entorno ---
@app.get("/debug-env")
async def debug_env():
    return {
        "ENV": ENV,
        "DATABASE_URL_present": bool(DATABASE_URL),
        "SUPABASE_URL_present": bool(SUPABASE_URL),
        "SUPABASE_KEY_present": bool(SUPABASE_KEY)
    }
