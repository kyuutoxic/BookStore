from flask.scaffold import F
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum
from enum import Enum as UserEnum
from datetime import datetime
from __init__ import db
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.sqltypes import DateTime
from flask_login import UserMixin


# Id autoincrement
class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMINISTRATOR = 1
    MANAGER = 2
    STOCKKEEPER = 3
    SELLER = 4
    CUSTOMER = 5


class User(BaseModel, UserMixin):

    __tablename__ = 'User'

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(255))
    active = Column(Boolean, default=True)
    join_date = Column(DateTime, default=datetime.now())
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.first_name


class BookLanguage(BaseModel):
    __tablename__ = 'book_language'

    name = Column(String(50), nullable=False)

    books = relationship("Book", backref="book_language", lazy=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    __tablename__ = 'category'

    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey(
        'parent_category.id'), nullable=False)

    books = relationship("Book", backref="category", lazy=True)

    def __str__(self):
        return self.name


class ParentCategory(BaseModel):
    __tablename__ = 'parent_category'

    name = Column(String(50), nullable=False)
    category = relationship('Category', backref="parent_category", lazy=True)

    def __str__(self):
        return self.name


class Book(BaseModel):
    __tablename__ = 'book'

    name = Column(String(255), nullable=False)
    language_id = Column(Integer, ForeignKey(
        'book_language.id'), nullable=False)
    num_pages = Column(Integer, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    publisher = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    image = Column(String(255))
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    imports = relationship("Import", backref="book", lazy=True)
    receipt_details = relationship('ReceiptDetail', backref='book', lazy=True)
    comments = relationship('Comment', backref='book', lazy=True)

    def __str__(self):
        return self.name


class Import(BaseModel):
    __tablename__ = 'import'

    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)
    quantities = Column(Integer, nullable=False)
    update_date = Column(DateTime, default=datetime.now())


class Receipt(BaseModel):
    __tablename__ = 'receipt'

    cus_name = Column(String(50), default=None)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('ReceiptDetail', backref='receipt', lazy=True)
    phone_number = Column(String(50))
    address_id = Column(Integer, ForeignKey('address.id'))
    active = Column(Integer, default=0)


class ReceiptDetail(BaseModel):
    __tablename__ = 'receipt_detail'

    receipt_id = Column(Integer, ForeignKey(Receipt.id),
                        nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id),
                     nullable=False, primary_key=True)
    quantity = Column(Integer, default=0, nullable=False)
    unit_price = Column(Float, nullable=False)


class Rule(BaseModel):
    __tablename__ = 'rule'

    name = Column(String(50), nullable=False)
    value = Column(Integer, nullable=False)


class Comment(BaseModel):
    __tablename__ = 'comment'

    content = Column(String(255), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    update_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class City(db.Model):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    district = relationship('District', backref='city', lazy=True)


class District(db.Model):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    city_id = Column(Integer, ForeignKey(City.id), nullable=False)


class Address(BaseModel):
    __tablename__ = 'address'

    street_name = Column(String(255), nullable=False)
    city_id = Column(Integer, ForeignKey(City.id), nullable=False)
    district_id = Column(Integer, ForeignKey(District.id), nullable=False)


if __name__ == '__main__':
    db.create_all()
