from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, String, Integer, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

engine = create_engine('postgresql://postgres:admin@localhost/example')
session = Session(bind=engine)
Base = declarative_base()
app = Flask(__name__)

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

Base.metadata.create_all(engine)

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
        return jsonify({"Success": "User has been added"})
    except:
        return jsonify({"Error": "User has not been added"})

@app.route('/user/', methods=['GET'])
def get_users():
    res = engine.execute(text("SELECT * FROM users ORDER BY id ASC"))
    lines = [dict(line) for line in res.fetchall()]
    return jsonify(lines)

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    res = engine.execute(text(f"SELECT * FROM users WHERE id = {id} ORDER BY id ASC"))
    lines = [dict(line) for line in res.fetchall()]
    return jsonify(lines)

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        u = session.query(Users).get(id)
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
        u = session.query(Users).get(id)
        session.delete(u)
        session.commit()
        return jsonify({"Success": f"User id{id} has been deleted"})
    except:
        return jsonify({"Error": f"User id{id} has not been deleted"})

if __name__ == '__main__':
    app.run(debug = True, port = 3000, host = '127.0.0.1')