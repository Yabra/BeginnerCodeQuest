import requests
import json

developer_password = input("Введите пароль разработчика: ")

response = requests.post(
    "http://127.0.0.1:5000/api/problems",
    json=json.dumps({
        "password": developer_password,
        "name": "0 + 1",
        "description": "Just 0 + 1",
        "tests": "[[\"0\", \"1\n\"]]",
        "points": 3
    })
)

json = response.json()
print(json)
