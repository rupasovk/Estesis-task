# Нужные библиотеки
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from contextlib import asynccontextmanager
from public.couriers import C_R
from public.orders import O_R

# занесение информации о включении и выключении в log.txt
@asynccontextmanager
async def lifespan(app: FastAPI):
    open("log.txt", mode="a").write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Begin\n')
    yield
    open("log.txt", mode="a").write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: End\n')

# Экземпляр FastAPI
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# включаем роутеры
app.include_router(C_R)
app.include_router(O_R)

# Начальная страница
@app.get('/')
def index():
    return FileResponse("files/index.html")