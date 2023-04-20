import requests

developer_password = input("Введите пароль разработчика: ")
request_id = input("Введите удаляемый id: ")

response = requests.delete(
    f"http://127.0.0.1:5000/api/problems?id={request_id}&password={developer_password}"
)

json = response.json()
print(json)
