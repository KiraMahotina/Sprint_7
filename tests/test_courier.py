import pytest
import requests
import allure
from utils.data_generator import generate_random_string, register_new_courier_and_return_login_password

BASE_URL = 'https://qa-scooter.praktikum-services.ru/api/v1/courier'

@allure.feature('Создание курьера')
class TestCourierCreation:
    @allure.title('Успешное создание курьера')
    def test_create_courier_success(self):
        login = generate_random_string(10)
        password = generate_random_string(10)
        first_name = generate_random_string(10)

        payload = {
            "login": login,
            "password": password,
            "firstName": first_name
        }

        with allure.step("Создать курьера"):
            response = requests.post(BASE_URL, data=payload)
            assert response.status_code == 201
            assert response.json() == {"ok": True}

        with allure.step("Удалить курьера"):
            auth_response = requests.post(
                f'{BASE_URL}/login',
                data={"login": login, "password": password}
            )
            courier_id = auth_response.json()['id']
            delete_response = requests.delete(f'{BASE_URL}/{courier_id}')
            assert delete_response.status_code == 200

    @allure.title('Создание двух одинаковых курьеров')
    def test_create_duplicate_courier_error(self):
        courier_data = register_new_courier_and_return_login_password()
        login, password, first_name = courier_data

        payload = {
            "login": login,
            "password": password,
            "firstName": first_name
        }

        response = requests.post(BASE_URL, data=payload)
        assert response.status_code == 409
        assert response.json()['message'] == 'Этот логин уже используется. Попробуйте другой.'

        auth_response = requests.post(
            f'{BASE_URL}/login',
            data={"login": login, "password": password}
        )
        courier_id = auth_response.json()['id']
        requests.delete(f'{BASE_URL}/{courier_id}')

    @allure.title('Создание курьера с отсутсвующим обязательным полем')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_create_courier_missing_field_error(self, missing_field):
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10)
        }
        del payload[missing_field]

        response = requests.post(BASE_URL, data=payload)
        assert response.status_code == 400, f"Тело ответа: {response.text}"


@allure.feature('Логин курьера')
class TestCourierLogin:
    @allure.title('Курьер может авторизоваться')
    def test_login_success(self):
        courier_data = register_new_courier_and_return_login_password()
        login, password, _ = courier_data

        response = requests.post(
            f'{BASE_URL}/login',
            data={"login": login, "password": password}
        )
        assert response.status_code == 200
        assert 'id' in response.json()

        courier_id = response.json()['id']
        requests.delete(f'{BASE_URL}/{courier_id}')

    @allure.title('Авторизация курьера с отсутсвующим обязательным полем')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_login_missing_field_error(self, missing_field):
        base_url = 'https://qa-scooter.praktikum-services.ru/api/v1/courier'

        payload = {"login": "", "password": ""}
        response = requests.post(
            f'{base_url}/login',
            json=payload,
            timeout=(30, 30)
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        assert response.status_code == 400
        assert response.json().get('message') == 'Недостаточно данных для входа'
        return


    @allure.title('Авторизация курьера с нправильными логин/пароль')
    def test_login_invalid_credentials_error(self):
        courier_data = register_new_courier_and_return_login_password()
        login, _, _ = courier_data

        response = requests.post(
            f'{BASE_URL}/login',
            data={"login": login, "password": "wrong"}
        )
        assert response.status_code == 404
        assert response.json()['message'] == 'Учетная запись не найдена'

        auth_response = requests.post(
            f'{BASE_URL}/login',
            data={"login": login, "password": courier_data[1]}
        )
        courier_id = auth_response.json()['id']
        requests.delete(f'{BASE_URL}/{courier_id}')
