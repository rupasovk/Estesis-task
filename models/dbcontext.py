# Нужные библиотеки
from sqlalchemy import Column, String, Integer, Identity, ForeignKey, Table, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

from enum import Enum

Base = declarative_base()

# Промежуточные таблицы
courier_mtm_district_table = Table(
    'courier_district',
    Base.metadata,
    Column('courier_id', ForeignKey('couriers.id')),
    Column('district_id', ForeignKey('districts.id')),
)

courier_mtm_order_table = Table(
    'courier_order',
    Base.metadata,
    Column('courier_id', ForeignKey('couriers.id')),
    Column('order_id', ForeignKey('orders.id')),
)

# Таблица курьеров
class Courier(Base):
    __tablename__ = 'couriers'
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String, index=True, nullable=False)
    
    dist = relationship("District", secondary=courier_mtm_district_table, cascade='save-update, merge, delete', passive_deletes=True)
    ord = relationship("Order", secondary=courier_mtm_order_table, cascade='save-update, merge, delete', passive_deletes=True)

# Таблица районов
class District(Base):
    __tablename__ = 'districts'
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String, index=True, nullable=False)

# Таблица заказов
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String, index=True, nullable=False)
    district = Column(String, index=True, nullable=False)
    status = Column(Integer, index=True, nullable=False)
    registration = Column(DateTime(timezone=False), default=datetime.now(),  index=True, nullable=False)
    completion = Column(DateTime(timezone=False), index=True, nullable=True)

class Tags(Enum):
    couriers = "couriers"
    orders = "orders"