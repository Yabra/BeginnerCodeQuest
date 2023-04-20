import requests

request_id = input("Введите искомый id: ")

response = requests.get(
    "http://127.0.0.1:5000/api/problems", {"id": request_id}
)

json = response.json()
for i in json.keys():
    print(json[i])
