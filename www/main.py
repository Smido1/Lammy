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
from loguru import logger
import sys
import os

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

db = SQLAlchemy(app)
jwt = JWTManager(app)

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | "
                              "<level>{level: <6}</level> | "
                              "<level>{message}</level>")

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coins = db.Column(db.Integer, nullable=False)
    last_click = db.Column(db.DateTime)
    time_out = db.Column(db.Integer)

    def __repr__(self):
        return f'<User {self.id} - {self.coins}>'


# Страницы
@app.route("/")
def index():
    return render_template("game.html")

@app.route("/store")
def store():
    return render_template("store.html")

@app.route("/upgrade")
def upgrade():
    return render_template("upgrades.html")

@app.route("/tasks")
def tasks():
    return render_template("tasks.html")


# API
@app.route("/logging", methods=["POST"])
def logging():
    data = request.get_json()
    user_id = data.get("user_id")
    logger.info("🚪 Начало логгинга пользователя " + str(user_id))

    if Users.query.filter_by(id=user_id).first():
        pass
    else:
        logger.info("➕ Создание нового пользователя")
        try:
            new_user = Users(id=user_id, coins=0, last_click=datetime.min)
            db.session.add(new_user)
            db.session.commit()
            logger.info("🤝 Пользователь создан")
        except:
            logger.error("Ошибка добавления пользователя")
            db.session.rollback()
            return jsonify({"status": "error", "message": "error while adding user"})

    access_token = create_access_token(identity=user_id)
    return jsonify({"status": "success", "message": "User logged!", "access_token": access_token})

@app.route("/get_values", methods=["GET"])
@jwt_required()
def get_values():

    current_user_id = get_jwt_identity()  # Получение текущего пользователя из JWT
    logger.info("📩 Запрос данных про пользователя " + str(current_user_id))
    user = Users.query.filter_by(id=current_user_id).first()
    last_click = user.last_click if user.last_click is not None else datetime.min
    remaining_time = user.time_out - (datetime.now() - last_click).total_seconds()
    remaining_time = round(remaining_time, 1)

    return jsonify({
        "status": "success",
        "score": user.coins,
        "remaining_time": remaining_time,
        "time_out": user.time_out
    })

@app.route("/click", methods=["POST"])
@jwt_required()
def click():
    logger.info("👇 Обработка нажатия кнопки пользователем " + str(get_jwt_identity()))
    current_user_id = get_jwt_identity()  # Получение текущего пользователя из JWT
    try:
        user = Users.query.filter_by(id=current_user_id).first()
        if (datetime.now() - user.last_click).total_seconds() >= user.time_out:
            user.coins += 1
            user.last_click = datetime.now()
            db.session.commit()
        else:
            logger.info("❌ Кнопка нажата слишком рано " + str(current_user_id))
            return jsonify({"status": "error", "message": "Too fast!"})
    except:
        logger.error("Ошибка обработки запроса нажатии кнопки")
        db.session.rollback()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Показывать только ошибки
    app.run(debug=True, ssl_context='adhoc')
