import pytest
import requests
import allure
from urls import ORDERS_URL

@allure.feature('Создание заказа')
class TestOrderCreation:
    BASE_URL = ORDERS_URL

    @allure.title('Создание заказа с разными цветами')
    @pytest.mark.parametrize('color', [['BLACK'], ['GREY'], ['BLACK', 'GREY'], []])
    def test_create_order_with_colors(self, color):
        payload = {
            "firstName": "Иван",
            "lastName": "Иванов",
            "address": "Москва, ул. Пушкина, 10",
            "metroStation": 4,
            "phone": "+79991234567",
            "rentTime": 3,
            "deliveryDate": "2024-06-10",
            "comment": "Тестовый заказ",
            "color": color
        }

        with allure.step("Отправить запрос на создание заказа"):
            response = requests.post(self.BASE_URL, json=payload)
            assert response.status_code == 201
            response_body = response.json()
            assert "track" in response_body
            assert isinstance(response_body["track"], int)

@allure.feature('Список заказов')
class TestOrderList:
    def test_get_order_list(self):
        with allure.step("Получить список всех заказов"):
            response = requests.get(ORDERS_URL)
            assert response.status_code == 200
            response_body = response.json()
            assert isinstance(response_body['orders'], list)
            if response_body['orders']:  # Если список не пустой
                assert all(key in response_body['orders'][0] for key in ['id', 'track'])
