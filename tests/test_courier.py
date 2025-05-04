import pytest
import requests
import allure
from utils.data_generator import generate_random_string
from urls import COURIER_URL

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
            response = requests.post(COURIER_URL, data=payload)
            assert response.status_code == 201
            assert response.json() == {"ok": True}

        # Удаление вынесено в отдельный шаг пост-условия
        with allure.step("Пост-условие: удалить тестового курьера"):
            auth_response = requests.post(
                f'{COURIER_URL}/login',
                data={"login": login, "password": password}
            )
            if auth_response.status_code == 200:
                courier_id = auth_response.json()['id']
                delete_response = requests.delete(f'{COURIER_URL}/{courier_id}')
                assert delete_response.status_code == 200
                assert delete_response.json() == {"ok": True}

    @allure.title('Создание двух одинаковых курьеров')
    def test_create_duplicate_courier_error(self, registered_courier):
        login, password, first_name = registered_courier

        payload = {
            "login": login,
            "password": password,
            "firstName": first_name
        }

        with allure.step("Отправить запрос с дублирующими данными"):
            response = requests.post(COURIER_URL, data=payload)
            assert response.status_code == 409
            assert response.json()['message'] == 'Этот логин уже используется. Попробуйте другой.'

    @allure.title('Создание курьера с отсутсвующим обязательным полем')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_create_courier_missing_field_error(self, missing_field):
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10)
        }
        del payload[missing_field]

        with allure.step("Отправить запрос на создание курьера"):
            response = requests.post(COURIER_URL, data=payload)
            assert response.status_code == 400
            response_body = response.json()
            assert "message" in response_body
            assert response_body["message"] == "Недостаточно данных для создания учетной записи"

@allure.feature('Логин курьера')
class TestCourierLogin:
    @allure.title('Курьер может авторизоваться')
    def test_login_success(self, registered_courier):
        login, password, _ = registered_courier

        with allure.step("Авторизоваться валидными данными"):
            response = requests.post(
                f'{COURIER_URL}/login',
                data={"login": login, "password": password}
            )
            assert response.status_code == 200
            response_body = response.json()
            assert "id" in response_body
            assert isinstance(response_body["id"], int)

    @allure.title('Авторизация курьера с отсутсвующим обязательным полем')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_login_missing_field_error(self, missing_field):
        payload = {"login": "", "password": ""}

        with allure.step("Отправить запрос на авторизацию без обязательного поля"):
            response = requests.post(
                f'{COURIER_URL}/login',
                json=payload,
                timeout=(30, 30)
            )

        assert response.status_code == 400
        response_body = response.json()
        assert "code" in response_body
        assert "message" in response_body
        assert response_body["message"] == "Недостаточно данных для входа"

    @allure.title('Авторизация курьера с неправильными логин/пароль')
    def test_login_invalid_credentials_error(self, registered_courier):
        login, _, _ = registered_courier

        with allure.step("Отправить запрос на авторизацию с неверным паролем"):
            response = requests.post(
                f'{COURIER_URL}/login',
                data={"login": login, "password": "wrong"}
            )

        assert response.status_code == 404
        response_body = response.json()
        assert "code" in response_body
        assert "message" in response_body
        assert response_body["message"] == "Учетная запись не найдена"
