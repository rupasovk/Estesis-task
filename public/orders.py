# Нужные библиотеки
from fastapi import APIRouter, Body, Depends, HTTPException
from typing import Annotated, Union
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models.models_order import *
from models.dbcontext import *
from public.db import get_session
from starlette import status
from sqlalchemy import select, insert, text, func
from datetime import datetime

# Создание роутера
O_R = APIRouter(tags = [Tags.orders], prefix = '/api/order')

# Публикация заказа в системе
@O_R.post("/", response_model = Union[Create_Order, New_Respons], tags=[Tags.orders], status_code=status.HTTP_201_CREATED)
async def create_order(item: Annotated[Add_Order, Body(embed = True, description = "Новый заказ")],
                DB: AsyncSession = Depends(get_session)):
    if (item.name is None or item.district is None):
            raise HTTPException(status_code=404, detail="Объект не определён")
    try:
        # Создание заказа
        order = Order(name = item.name, district = item.district, status = 1)
        # Получаем id будущего заказа
        id_o = await (DB.scalar(select(func.max(Order.id))))
        if id_o == None:
            id_o = 1
        else:
            id_o+= 1
        # Получаем id района, где находится заказ
        id_d = await (DB.scalar(select(District.id).where(District.name == order.district)))
        # Ищем курьеров, работающих в данном районе
        if id_d == None:
            return JSONResponse(status_code=404, content={"message": "Курьер не найден"})
        else:
            couriers = await (DB.scalars(text(f"select courier_id from courier_district where district_id = {id_d};")))
        couriers = couriers.all()
        # Ищем свободного курьера
        for i in couriers:
            orders = await (DB.scalars(text(f"select order_id from courier_order where courier_id = {i};")))
            orders = orders.all()
            if orders == []: # Нашли свободного курьера
                await DB.execute(insert(Order).values({"name": order.name, "district": order.district, "status": order.status}))
                await DB.commit()
                buffer = courier_mtm_order_table.insert().values(courier_id=i, order_id=id_o)
                await DB.execute(buffer)
                await DB.commit()
                order = {"courier_id": i, "order_id": id_o}
                return order
            else: # Проверяем, что у курьера выполнены все заказы
                col = 0
                count = len(orders)
                for j in orders:
                    buff = await DB.scalar(select(Order.status).where(Order.id == j))
                    if buff == 2:
                        col+=1
                # Курьер выполнил все свои заказы
                if col == count:
                    # Нашли свободного курьера
                    await DB.execute(insert(Order).values({"name": order.name, "district": order.district, "status": order.status}))
                    await DB.commit()
                    buffer = courier_mtm_order_table.insert().values(courier_id=i, order_id=id_o)
                    await DB.execute(buffer)
                    await DB.commit()
                    order = {"courier_id": i, "order_id": id_o}
                    return order
        # Нет свободного курьера
        return JSONResponse(status_code=404, content={"message": "Курьер не найден"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка в добавлении объекта {order}")
    
# Получение информации о заказе
@O_R.get("/{id}", response_model = Union[Secondary_Order, New_Respons], tags=[Tags.orders])
async def get_order(id: int, DB: AsyncSession = Depends(get_session)):
    try:
        order = await DB.execute(select(Order).where(Order.id == id))
        return order.scalars().one()
    except Exception as e:
        return JSONResponse(status_code=404, content={"message": "Заказ не найден"})

# Завершить заказ 
@O_R.post("/{id}", response_model = New_Respons, tags=[Tags.orders])
async def complete_order(id: int, DB: AsyncSession = Depends(get_session)):
    try: # Ищем заказ   
        order = await DB.execute(select(Order).where(Order.id == id))
        result = order.scalars().one()
    except Exception as e: # Заказ не найден
        return JSONResponse(status_code=404, content={"message": "Заказ не найден"})
    print(result.status)
    if result.status == 2: # Заказ уже завершен
        return JSONResponse(status_code=208, content={"message": "Заказ уже завершен"})
    try: # Меняем статус заказа на завершенный
        await DB.execute(text(f"update orders set status=2, completion=\'{datetime.now()}\' where id={id};"))
        await DB.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка в изменении объекта {result}")
    return JSONResponse(status_code=200, content={"message": "Заказ завершен"})