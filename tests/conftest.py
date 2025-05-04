import pytest
import requests
import allure
from urls import COURIER_URL
from utils.data_generator import register_new_courier_and_return_login_password


@pytest.fixture
def registered_courier():
    """Фикстура для регистрации и последующего удаления тестового курьера"""
    courier_data = register_new_courier_and_return_login_password()
    yield courier_data

    # Пост-условие: удаление курьера
    login, password, _ = courier_data
    with allure.step("Пост-условие: удаление тестового курьера"):
        auth_response = requests.post(
            f'{COURIER_URL}/login',
            data={"login": login, "password": password}
        )
        if auth_response.status_code == 200:
            courier_id = auth_response.json()['id']
            requests.delete(f'{COURIER_URL}/{courier_id}')
