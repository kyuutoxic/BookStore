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

    __tablename__ = 'user'

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
    parent_id = Column(Integer, ForeignKey('parent_category.id'), nullable=False)

    books = relationship("Book", backref="category", lazy=True)
    # children_book = relationship('Children_Book', backref="children_category", lazy=True)

    def __str__(self):
        return self.name


class ParentCategory(BaseModel):
    __tablename__ = 'parent_category'
    
    name = Column(String(50), nullable=False)
    category = relationship('Category', backref="parent_category", lazy=True)
    # parent_book = relationship("Parent_Book", backref="parent_category", lazy=True)

    def __str__(self):
        return self.name


class Book(BaseModel):
    __tablename__ = 'book'

    name = Column(String(255), nullable=False)
    language_id = Column(Integer, ForeignKey('book_language.id'), nullable=False)
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
    # parent_book = relationship('ParentCategory',secondary='parent_book',lazy='subquery',backref=backref('book', lazy=True))
    # children_book = relationship('ChildrenCategory',secondary='children_book',lazy='subquery',backref=backref('book', lazy=True))

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
    # details = relationship('ReceiptDetail', backref='receipt', lazy=True)
    active = Column(Boolean, default=False)


class ReceiptDetail(BaseModel):
    __tablename__ = 'receipt_detail'

    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0,nullable=False)


class Rule(BaseModel):
    __tablename__ = 'rule'

    name = Column(String(50), nullable=False)
    value = Column(Integer, nullable=False)   


if __name__ == '__main__':
    db.create_all()