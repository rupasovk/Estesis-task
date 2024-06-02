# Нужные библиотеки
from pydantic import BaseModel, Field
from typing import Annotated, Union

# Главная модель для таблицы заказов
class Main_Order(BaseModel):
    id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None
    name: Union[str, None] = None
    district: Union[str, None] = None
    status: Union[int, None] = None


# Модель для регистрации заказов
class Add_Order(BaseModel):
    name: Union[str, None] = None
    district: Union[str, None] = None

# Модель для связывания курьера и заказа
class Create_Order(BaseModel):
    courier_id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None
    order_id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None

# Минимальная информация о заказе
class Secondary_Order(BaseModel):
    id: Annotated[Union[int, None], Field(default=100, ge=0, lt=200)] = None
    status: Union[int, None] = None

# Модель для текстового ответа
class New_Respons(BaseModel):
    message: str