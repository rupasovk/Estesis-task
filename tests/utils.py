import pytest

# Тестовый курьер
@pytest.fixture()
async def create_courier(client):
    courier = {
        "item": {
            "name": "Иван Иванов",
            "districts": [
                "Железнодорожный", "Центральный"
                          ]
        }
    }
    response = await client.post("/api/courier/", json=courier)
    new_courier_id = response.json()['id']
    return new_courier_id

# Тестовый заказ
@pytest.fixture()
async def create_order(client):
    order = {
        "item": {
            "name": "Продукты",
            "district": "Железнодорожный"
        }
    }
    response = await client.post("/api/order/", json=order)
    print(response.json())
    new_order_id = response.json()['order_id']
    return new_order_id