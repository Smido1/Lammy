#TODO
# - [ ] Передавать в Flask не сырой id, а UUID, который будет расшифрован и сопоставлен
# - [x] Сохранять состояние кнопки в БД после нажатия, для препятствия сброса таймера после перезагрузки 
# - [ ] Получить состояние таймера после перезагрузки
# - [ ] Вкладки: игра, улучшения, таски, магазин

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

db = SQLAlchemy(app)
jwt = JWTManager(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coins = db.Column(db.Integer, nullable=False)
    last_click = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.id} - {self.coins}>'


@app.route("/")
def index():
    # user_id = request.args.get("user_id")
    # access_token = create_access_token(identity=user_id)
    
    # if Users.query.filter(Users.id == user_id).all():
    #     pass
    # else:
    #     try:
    #         new_user = Users(id=user_id, coins=0)
    #         db.session.add(new_user)
    #         db.session.commit()
    #     except:
    #         db.session.rollback()
    
    return render_template("index.html")

@app.route("/logging", methods=["POST"])
def logging():
    data = request.get_json()
    user_id = data.get("user_id")
    if Users.query.filter_by(id=user_id).first():
        pass
    else:
        try:
            new_user = Users(id=user_id, coins=0)
            db.session.add(new_user)
            db.session.commit()
        except:
            db.session.rollback()
    
    access_token = create_access_token(identity=user_id)
    return jsonify({"status": "success", "message": "User logged!", "access_token": access_token})

@app.route("/get_values", methods=["GET"])
@jwt_required()
def get_values():
    current_user_id = get_jwt_identity()  # Получение текущего пользователя из JWT
    user = Users.query.filter_by(id=current_user_id).first()
    return jsonify({
        "status": "success",
        "score": user.coins
    })

@app.route("/click", methods=["POST"])
@jwt_required()
def click():
    current_user_id = get_jwt_identity()  # Получение текущего пользователя из JWT
    try:
        user = Users.query.filter_by(id=current_user_id).first()
        if (datetime.now() - user.last_click).total_seconds() >= 20:
            user.coins += 1
            user.last_click = datetime.now()
        db.session.commit()
    except:
        print("error")
        db.session.rollback()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')
