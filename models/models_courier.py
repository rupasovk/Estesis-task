# Нужные библиотеки
from pydantic import BaseModel, Field
from typing import Annotated, Union
from datetime import time

# Главная модель для таблицы курьеров
class Main_Courier(BaseModel):
    id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None
    name: Union[str, None] = None
    districts: Union[list[str], None] = None

# Модель для регистрации курьера
class Add_Courier(BaseModel):
    name: Union[str, None] = None
    districts: Union[list[str], None] = None

# Минимальная информация о курьере
class Secondary_Courier(BaseModel):
    id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None
    name: Union[str, None] = None

# Полная информация о курьере
class Return_Courier(BaseModel):
    id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None
    name: Union[str, None] = None
    districts: Union[list[str], None] = None
    active_order: Union[dict, None] = None
    avg_order_complete_time: Union[time, None] = None
    avg_day_orders: Union[int, None] = None

# Модель для текстового ответа
class New_Respons(BaseModel):
    message: str