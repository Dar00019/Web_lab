from requests import get, post, put, delete
from pprint import pprint

# Тестирование GET
'''
result = get("http://127.0.0.1:5000/api/users").json()
pprint(result)

result = get("http://127.0.0.1:5000/api/news").json()
pprint(result)
'''

# Тестирование POST
'''
new_user = {"name": "Новый пользователь",
            "email": "u123@mail.ru",
            "password": "12345"}

result = post("http://127.0.0.1:5000/api/users", json=new_user).json()
pprint(result)

new_news = {"header": "Новая новость",
            "text": "Проверяю API",
            "user_id": 4}

result = post("http://127.0.0.1:5000/api/news", json=new_news).json()
pprint(result)
'''


# Тестирование PUT
'''
user = {"name": "Изменённое с помощью API имя"}
result = put("http://127.0.0.1:5000/api/users/4", json=user).json()
pprint(result)

news = {"header": "И заголовок новости с помощью API"}
result = put("http://127.0.0.1:5000/api/news/5", json=news).json()
pprint(result)
'''

# Тестирование DELETE
'''
result = delete("http://127.0.0.1:5000/api/users/4").json()
pprint(result)

result = delete("http://127.0.0.1:5000/api/news/5").json()
pprint(result)
'''