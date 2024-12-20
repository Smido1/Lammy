from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clicker_bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80))
    score = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.get_json()
    score = data.get("score")
    level = data.get("level")
    # Здесь можно сохранить данные в базу или файл
    return jsonify({"status": "success", "message": "Score updated!"})


if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')
