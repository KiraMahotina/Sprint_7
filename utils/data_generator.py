import requests
import random
import string

def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def register_new_courier_and_return_login_password():
    login = generate_random_string(10)
    password = generate_random_string(10)
    first_name = generate_random_string(10)

    payload = {
        "login": login,
        "password": password,
        "firstName": first_name
    }

    response = requests.post(
        'https://qa-scooter.praktikum-services.ru/api/v1/courier',
        data=payload
    )

    if response.status_code == 201:
        return [login, password, first_name]
    return []
