# у тебя в репозитории есть папки .idea и __pycache__, они тебе не нужны, это лишний мусор. В гите
# надо хранить только код который ты сам пишешь. Почитай про .gitignore и добавь его к себе.

# все python файлы лучше хранить в папке app, а в корне репозитория всякие дополнительный файлы, типа
# .gitignore и requirements
# -- app
# ----- app.py
# ----- database.py
# ----- routes.py
# -- .gitginore
# -- requirements.txt


# а как я узнаю какой версии зависимости мне нужны? Почитай про requirements.txt и добавь его к себе
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, String, Integer, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

# Подключение к базе надо вынести в отдельный файл

# Данные для подключения к базе должны храниться отдельно и раздельно
# pg_user = admin
# pg_host = localhost
# etc...
engine = create_engine('postgresql://postgres:admin@localhost/example')
session = Session(bind=engine)
Base = declarative_base()

# Созднаие app и его запуск также в отдельном файле
app = Flask(__name__)

# Модели базы данных тоже в отдельном файле
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement="auto")
    username = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))

    def __repr__(self):
        return f"<users {self.id}>"

# это пока можно делать в файле где создается flask app
Base.metadata.create_all(engine)

# роуты также в отдельном файле
@app.route('/user/', methods=['POST'])
def add_user():
    try:
        new_user = Users(
            username=request.json['username'],
            password=generate_password_hash(request.json['password']),
            email=request.json['email'],
            first_name=request.json['first_name'],
            last_name=request.json['last_name']
        )
        session.add(new_user)
        session.commit()

        # Круто. Вот представь я создал пользователя и ты мне ответил красава, ты всё создал. Я такой окей, теперь
        # я хочу получить данные по своему созданному пользователю и... иду нахуй, т.к. я не знаю id пользователя который
        # создался. Единственный вариант через get запрос получать всех вообще пользователей и искать своего
        return jsonify({"Success": "User has been added"})
    except:
        return jsonify({"Error": "User has not been added"})

@app.route('/user/', methods=['GET'])
def get_users():
    # без чистых SQL запросов
    # engine здесь не должен нигде использоваться кроме как создание сессии. Все запросы надо выполнять через session
    res = engine.execute(text("SELECT * FROM users ORDER BY id ASC"))
    lines = [dict(line) for line in res.fetchall()]
    return jsonify(lines)

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    # никакого чистого SQL. Если ты используешь sqlalchemy, то используй её везде. Это тоже самое что
    # ты строишь дом из кирпича, но в некоторых местах глину ёбнул, потому что лень было искать как кирпич положить
    res = engine.execute(text(f"SELECT * FROM users WHERE id = {id} ORDER BY id ASC"))
    lines = [dict(line) for line in res.fetchall()]
    return jsonify(lines)

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        u = session.query(Users).get(id)
        # а если я сделаю запрос {"username": "blabla", "fist_name": "aaa"}? Что произойдет с остальными полями?
        u.username = request.json['username']
        u.password = generate_password_hash(request.json['password'])
        u.email = request.json['email']
        u.first_name = request.json['first_name']
        u.last_name = request.json['last_name']

        session.add(u)
        session.commit()
        return jsonify({"Success": f"User id{id} has been updated"})
    except:
        return jsonify({"Error": f"User id{id} has not been updated"})

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        # а если я здесь попытаюсь удалить пользователя с id, которого не существует?
        u = session.query(Users).get(id)
        session.delete(u)
        session.commit()
        return jsonify({"Success": f"User id{id} has been deleted"})
    except:
        return jsonify({"Error": f"User id{id} has not been deleted"})

if __name__ == '__main__':
    app.run(debug = True, port = 3000, host = '127.0.0.1')