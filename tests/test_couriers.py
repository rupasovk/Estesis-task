from fastapi import status
from utils import create_courier

# Проверка получения списка курьеров
# Код состояния - 404
async def test_get_couriers_http_404_not_found(client):
    detail = "Курьеры не найдены"
    response = await client.get("/api/courier/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert detail == response.json()['message']
# Код состояния - 200
async def test_get_couriers(client, create_courier):
    response = await client.get("/api/courier/")
    assert response.status_code == status.HTTP_200_OK

# Проверка получения курьера по id
# Код состояния - 200
async def test_get_courier(client, create_courier):
    courier_id = create_courier
    response = await client.get(f"/api/courier/{courier_id}")
    assert response.status_code == status.HTTP_200_OK
    assert courier_id == response.json()['id']
# Код состояния - 404
async def test_get_courier_http_404_not_found(client):
    courier_id = 0
    detail = "Курьер не найден"
    response = await client.get(f"/api/courier/{courier_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert detail == response.json()['message']