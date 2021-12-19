from models import User
from flask import request
import hashlib
from models import Category, Book, ParentCategory, Import, Receipt, ReceiptDetail, Rule
from sqlalchemy import func
from __init__ import db


def get_user_by_id(user_id):
    return User.query.get(user_id)


#check username and password
def check_login(username, password):
    if username and password:
        password =str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
       
        return User.query.filter(User.username == username.strip(), User.password == password).first()


def category_stats(parent=None):
    parent = request.args.get('parent')

    return db.session.query(Category.id, Category.name, Category.parent_id,
                            func.count(Book.id))\
                     .join(Book,
                           Book.category_id.__eq__(Category.id))\
                    .filter(Category.parent_id.__eq__(parent))\
                     .group_by(Category.id, Category.name).all()


def read_parentCategory():
    return ParentCategory.query.all()


def read_book(kw=None):
    books = Book.query

    if kw:
        books = books.filter(Book.name.contains(kw))

    return books.all()


def get_book(book_id):
    return Book.query.get(book_id)


def add_import(book_id, quantities):
    imports = Import(book_id=book_id, quantities=quantities)
    db.session.add(imports)
    db.session.commit()


def read_import():
    return  Import.query.all()


def get_rule(rule_id):
    return Rule.query.get(rule_id)


def add_receipt(user_id, cus_name=None):
    receipt = Receipt(user_id=user_id, cus_name=cus_name)
    db.session.add(receipt)
    db.session.commit()


def read_receipt_by_active():
    return db.session.query(Receipt.id)\
                    .filter(Receipt.active == False).all()


def add_receiptdetails(receipt_id, book_id, quantity):
    receipt_details = ReceiptDetail(receipt_id=receipt_id, book_id=book_id, quantity=quantity)
    db.session.add(receipt_details)
    db.session.commit()


# def get_add_receiptdetails():
#     return ReceiptDetail.query.all()
def update_quantity_receipt_details(receipt_detail_id, quantity):
    a = get_receiptdetails_by_id(receipt_detail_id)
    a.quantity = a.quantity + quantity
    db.session.commit()


def get_receiptdetails_by_id(receipt_detail_id):
    return ReceiptDetail.query.get(receipt_detail_id)


def read_receiptdetails_by_receipt_id(receipt_id):
    return ReceiptDetail.query.filter(ReceiptDetail.receipt_id == receipt_id).all()


def get_receipt_by_id(receipt_id):
    return Receipt.query.get(receipt_id)


def update_receipt_status(receipt_id):
    receipt = Receipt.query.get(receipt_id).active = True
    db.session.commit()


def del_receipt_detail(receipt_detail_id):
    ReceiptDetail.query.filter(ReceiptDetail.id == receipt_detail_id).delete()
    db.session.commit()


def update_stock(book_id, quantity):
    book = Book.query.get(book_id)
    book.quantity = book.quantity - quantity
    db.session.commit()





