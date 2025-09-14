from fastapi import FastAPI, HTTPException
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)

@app.get("/")
async def root():
    return {"mensaje": "API de Razas de Perros funcionando ✅"}

@app.get("/razas")
async def listar_razas():
    conn = await get_connection()
    rows = await conn.fetch("SELECT * FROM razas_perros")
    await conn.close()
    return [dict(r) for r in rows]

@app.get("/razas/{id}")
async def obtener_raza(id: int):
    conn = await get_connection()
    row = await conn.fetchrow("SELECT * FROM razas_perros WHERE id = $1", id)
    await conn.close()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Raza no encontrada")

@app.post("/razas")
async def crear_raza(nombre: str, origen: str, tamanio: str, esperanza_vida: int):
    conn = await get_connection()
    row = await conn.fetchrow("""
        INSERT INTO razas_perros (nombre, origen, tamanio, esperanza_vida)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """, nombre, origen, tamanio, esperanza_vida)
    await conn.close()
    return dict(row)
