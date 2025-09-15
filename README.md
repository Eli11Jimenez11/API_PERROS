*API en línea*

*Base URL:* https://api-perros.vercel.app/

*Postman:* https://eli11jimenez11-1997738.postman.co/workspace/Elizabeth-'s-Workspace~4fbcd19e-0721-4e7e-8e19-468682c17278/collection/48439553-75fbfd9c-cdf7-4cf6-ba24-f5b0373afdae?action=share&creator=48439553

*Tecnologías utilizadas:*
Backend: Python 3.11, FastAPI
Base de datos: PostgreSQL (Supabase)
Despliegue: Vercel
Conexión remota: Supabase REST API en producción y asyncpg para entorno local
Variables de entorno: ENV, DATABASE_URL, SUPABASE_URL, SUPABASE_KEY


*Configuración del entorno local*

git clone https://github.com/Eli11Jimenez11/API_PERROS.git

*Crea un entorno virtual:*
python -m venv venv
venv\Scripts\activate  

*Instala dependencias:*
pip install -r requirements.txt

*Crea archivo .env con las variables de entorno:*
DATABASE_URL=postgresql://postgres:Elizabeth.1020111485@db.tjtlyfnorrncyrjdyhff.supabase.co:5432/postgres?sslmode=require
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqdGx5Zm5vcnJuY3lyamR5aGZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4NjgwNzksImV4cCI6MjA3MzQ0NDA3OX0.wvn6T_Wxt2UeWTuvbHHbTYjgUHe6RXRZF2UiV1DQXT4
SUPABASE_URL=https://tjtlyfnorrncyrjdyhff.supabase.co
ENV=production

*Ejecutar la API localmente:*
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000

*Crea las siguientes variables de entorno en el dashboard de Vercel:*
DATABASE_URL=postgresql://postgres:Elizabeth.1020111485@db.tjtlyfnorrncyrjdyhff.supabase.co:5432/postgres?sslmode=require
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqdGx5Zm5vcnJuY3lyamR5aGZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc4NjgwNzksImV4cCI6MjA3MzQ0NDA3OX0.wvn6T_Wxt2UeWTuvbHHbTYjgUHe6RXRZF2UiV1DQXT4
SUPABASE_URL=https://tjtlyfnorrncyrjdyhff.supabase.co
ENV=production


*Crea el archivo vercel.json*
{
  "version": 2,
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "api/index.py" }
  ],
  "devCommand": "uvicorn api.index:app --reload --host 0.0.0.0 --port $PORT"
}

*Desplegar:*
vercel --prod

*Estructura del proyecto:*
api-perros/
│
├─ api/
│   └─ index.py        # Archivo principal de la API
│
├─ requirements.txt    # Dependencias del proyecto
├─ vercel.json         # Configuración de rutas y despliegue en Vercel
└─ README.md     