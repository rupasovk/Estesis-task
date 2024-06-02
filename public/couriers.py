# Нужные библиотеки
from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Annotated, Union
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models.models_courier import *
from models.dbcontext import *
from public.db import get_session
from starlette import status
from sqlalchemy import select, insert, text, func
from datetime import timedelta, datetime

# Создание роутера
C_R = APIRouter(tags = [Tags.couriers], prefix = '/api/courier')

# Регистрация курьера в системе
@C_R.post("/", response_model = Union[Main_Courier, New_Respons], tags=[Tags.couriers], status_code=status.HTTP_201_CREATED)
async def create_courier(item: Annotated[Add_Courier, Body(embed = True, description = "Новый курьер")],
                DB: AsyncSession = Depends(get_session)):
    if (item.name is None or item.districts is None):
            raise HTTPException(status_code=404, detail="Объект не определён")
    try:
        # Добавление курьера
        courier = Courier(name = item.name)
        await DB.execute(insert(Courier).values({"name": courier.name}))
        await DB.commit() 
        # Добавление районов
        for k in item.districts:
            buff = await DB.execute(select(District.name).where(District.name == k))
            result = buff.scalars().all()
            if k not in result:
                district = District(name = k)
                DB.add(district)
                await DB.commit()
        # Соединение курьера и районов
        id_c = await (DB.scalar(select(func.max(Courier.id))))
        for k in item.districts:
            id_d = await DB.scalar(select(District.id).where(District.name == k))
            statement = courier_mtm_district_table.insert().values(courier_id=id_c, district_id=id_d)
            await DB.execute(statement)
            await DB.commit()
        # Возвращаем добавленного курьера
        courier = {"id": id_c, "name": item.name, "districts": item.districts}
        return courier
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка в добавлении объекта {courier}")

# Получение информации обо всех курьерах в системе
@C_R.get("/", response_model = Union[list[Secondary_Courier], New_Respons], tags=[Tags.couriers])
async def get_couriers_db(DB: AsyncSession = Depends(get_session)):
    couriers = await DB.execute(select(Courier).order_by(Courier.id.asc()))
    result = couriers.scalars().all()
    if result == []:
        return JSONResponse(status_code=404, content={"message": "Курьеры не найдены"})
    return result

def convert_seconds(seconds):
    return str(timedelta(seconds=seconds))

# Получение подробной информации о курьере
@C_R.get("/{id}", response_model = Union[Return_Courier, New_Respons], tags=[Tags.couriers])
async def get_courier(id: int, DB: AsyncSession = Depends(get_session)):
    try:
        # Получение курьера
        courier = await DB.execute(text(f"select * from couriers where id = {id};"))
        courier = courier.all()[0]
        # Получение районов, в которых он работает
        districts = await DB.scalars(text(f"select name from districts where id in (select courier_district.district_id from courier_district where courier_district.courier_id = {id});"))
        districts = districts.all()
        # Получение активного заказа
        order = await DB.execute(text(f"select id, name from orders where id in (select order_id from courier_order where courier_id = {id}) and status = 1;"))
        order = order.all()
        # Получение среднего кол-ва завершенных заказов в день
        buff = await DB.execute(text(f"SELECT date_trunc('day', completion) as day_start, COUNT(*) FROM orders WHERE status = 2 AND id IN(SELECT order_id FROM courier_order WHERE courier_id={id}) GROUP BY 1 ORDER BY 1;"))
        buff = buff.all()
        day_or = 0
        if buff != []:
            sum = 0
            for i in range(len(buff)):
                sum+=buff[i][1]
            day_or = int(sum/len(buff))
        # Получение среднего времени отработки заказа
        buff = await DB.execute(text(f"SELECT completion-registration as time FROM orders WHERE status = 2 AND id IN(SELECT order_id FROM courier_order WHERE courier_id={id});"))
        buff = buff.all()
        time_or = 0
        if buff != []:
            sum = timedelta(hours=0, minutes=0, seconds=0, microseconds=0)
            for i in range(len(buff)):
                sum+=buff[i][0]
            time_or = int(sum.total_seconds()/len(buff))
        time_or = convert_seconds(time_or)
        time_or = datetime.strptime(time_or, '%H:%M:%S').strftime("%H:%M:%S")
        
        if order == []: # Нет активного заказа
            result = {"id": courier[0], "name": courier[1], "districts": districts, "avg_order_complete_time":time_or, "avg_day_orders": day_or}
        else: # Есть активный заказ
            order = order[0]
            result = {"id": courier[0], "name": courier[1], "districts": districts, "active_order": {"order_id": order[0], "order_name": order[1]}, "avg_order_complete_time":time_or, "avg_day_orders": day_or}
        return result
    except Exception as e:
        return JSONResponse(status_code=404, content={"message": "Курьер не найден"})