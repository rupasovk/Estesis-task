from fastapi import status
from utils import create_order

# Проверка получения заказа по id
# Код состояния - 200
async def test_get_order(client, create_order):
    order_id = create_order
    response = await client.get(f"/api/order/{order_id}")
    assert response.status_code == status.HTTP_200_OK
    assert order_id == response.json()['id']
# Код состояния - 404
async def test_get_order_http_404_not_found(client):
    order_id = 0
    detail = "Заказ не найден"
    response = await client.get(f"/api/order/{order_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert detail == response.json()['message']

# Завершение заказа
# Код состояния - 200
async def test_post_order(client):
    order_id = 1
    response = await client.post(f"/api/order/{order_id}")
    assert response.status_code == status.HTTP_200_OK
# Код состояния - 404
async def test_post_order_http_404_not_found(client):
    order_id = 0
    detail = "Заказ не найден"
    response = await client.post(f"/api/order/{order_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert detail == response.json()['message']
# Код состояния - 208
async def test_post_order_http_204(client):
    order_id = 1
    detail = "Заказ уже завершен"
    response = await client.post(f"/api/order/{order_id}")
    assert response.status_code == status.HTTP_208_ALREADY_REPORTED
    assert detail == response.json()['message']