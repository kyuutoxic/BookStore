from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
import cloudinary.uploader


app = Flask(__name__)

# Database
app.secret_key = 'NguyenVanLam/NguyenHoangTrungThong/LeTuanDat/TranMinhHuy'
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:123456@localhost/dbappbook?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
# app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
# app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite: ///dbappbook.db'
app.config['COMMENT_SIZE'] = 20 


db = SQLAlchemy(app=app)

login = LoginManager(app=app)

cloudinary.config(
    cloud_name = 'djgexdpxq',
    api_key = '564911839957893',
    api_secret = 'Z5PxnO3G75eMDuoN_itQEn9GImc'
)

