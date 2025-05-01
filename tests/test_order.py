import pytest
import requests
import allure

@allure.feature('Создание заказа')
class TestOrderCreation:
    BASE_URL = 'https://qa-scooter.praktikum-services.ru/api/v1/orders'

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

        response = requests.post(self.BASE_URL, json=payload)
        assert response.status_code == 201
        assert 'track' in response.json()

@allure.feature('Список заказов')
class TestOrderList:
    def test_get_order_list(self):
        response = requests.get('https://qa-scooter.praktikum-services.ru/api/v1/orders')
        assert response.status_code == 200
        assert isinstance(response.json()['orders'], list)
