from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

# Database
app.secret_key = 'NguyenVanLam/NguyenHoangTrungThong/LeTuanDat/TranMinhHuy'
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:123456@localhost/dbappbook?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
# app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

db = SQLAlchemy(app=app)

login = LoginManager(app=app)

