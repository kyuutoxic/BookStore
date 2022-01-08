from models import User
from flask import request, session
import hashlib
from models import Category, Book, ParentCategory, Import, Receipt, ReceiptDetail, Rule, BookLanguage, Comment
from sqlalchemy import func
from __init__ import db, app
from flask_login import current_user
from sqlalchemy.sql import extract



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


def add_receiptdetails(receipt_id, book_id, quantity, unit_price):
    receipt_details = ReceiptDetail(receipt_id=receipt_id, book_id=book_id, quantity=quantity, unit_price=unit_price)

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


# Client func
def read_parent_category():
    return ParentCategory.query.all()


def read_books():
    return Book.query.all()


def get_book_by_id(book_id):
    book = Book.query

    for b in book:
        if b.id == book_id:
            return b


def get_language_by_id(language_id):
    return BookLanguage.query.get(language_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_username(username):
    user = User.query.all()
    for u in user:
        if u.username == username:
            return False
    return True
    

def add_user(firstname, lastname,email, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(first_name=firstname.strip(),
                last_name=lastname.strip(),
                email=email.strip(),
                username=username.strip(),
                password=password,
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def cart_stats(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def add_receipts(cart):
    if cart:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)
        db.session.commit()

        for c in cart.values():
            detail = ReceiptDetail(receipt_id=receipt.id,
                                   book_id=c['id'],
                                   quantity=c['quantity'],unit_price=c['price'])
            db.session.add(detail)

        db.session.commit()


def load_products(category_id=None, kw=None,page = 1):
    products = Book.query
    
    if category_id == None:
        category_id = '0'
      
    if category_id:
        if category_id == str(0):
            products = Book.query
        else:
            # cate = Category.query.filter(Category.id == category_id)
            products = products.filter(Book.category_id.__eq__(category_id))
            # products = db.session.query()

    if kw:
        products = products.filter(Book.name.contains(kw))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return products.slice(start, end).all()


def count_products(category_id=0, kw=None):
    products = Book.query
    if category_id == None:
        category_id = '0'
      
    if category_id:
        if category_id == str(0):
            products = Book.query
        else:
            products = products.filter(Book.category_id.__eq__(category_id))

    if kw:
        products = products.filter(Book.name.contains(kw))

    return products.count()


def add_comment(content, book_id):
    c = Comment(content=content, book_id=book_id, user=current_user)

    db.session.add(c)
    db.session.commit()
    
    return c


def get_comment(book_id, qttcomment):
    return Comment.query.filter(Comment.book_id.__eq__(book_id) ).order_by(-Comment.id).slice(0, qttcomment).all()


def count_comments(book_id):
    return Comment.query.filter(Comment.book_id.__eq__(book_id)).count()



def get_name_cate(category_id):
    if category_id == None:
        category_id = '0'
    if category_id == str(0):
        return 'All products'
    else:
        return ParentCategory.query.get(category_id)
 


def get_name_category_by_id(category_id):
    return Category.query.get(category_id)



def get_name_parentcategory_by_id(parent_id):
    return ParentCategory.query.get(parent_id)


def product_month_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
                     .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id))\
                     .filter(extract('year', Receipt.created_date) == year)\
                     .group_by(extract('month', Receipt.created_date))\
                     .order_by(extract('month', Receipt.created_date)).all()


from models import User
from flask import request, session
import hashlib
from models import Category, Book, ParentCategory, Import, Receipt, ReceiptDetail, Rule, BookLanguage, Comment
from sqlalchemy import func
from __init__ import db, app
from flask_login import current_user
from sqlalchemy.sql import extract



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


# Client func
def read_parent_category():
    return ParentCategory.query.all()


def read_books():
    return Book.query.all()


def get_book_by_id(book_id):
    book = Book.query

    for b in book:
        if b.id == book_id:
            return b


def get_language_by_id(language_id):
    return BookLanguage.query.get(language_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_username(username):
    user = User.query.all()
    for u in user:
        if u.username == username:
            return False
    return True
    

def add_user(firstname, lastname,email, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(first_name=firstname.strip(),
                last_name=lastname.strip(),
                email=email.strip(),
                username=username.strip(),
                password=password,
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def cart_stats(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def add_receipts(cart):
    if cart:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)
        db.session.commit()

        for c in cart.values():
            detail = ReceiptDetail(receipt_id=receipt.id,
                                   book_id=c['id'],
                                   quantity=c['quantity'],unit_price=c['price'])
            db.session.add(detail)

        db.session.commit()


def load_products(category_id=None, kw=None,page = 1):
    products = Book.query
    
    if category_id == None:
        category_id = '0'
      
    if category_id:
        if category_id == str(0):
            products = Book.query
        else:
            # cate = Category.query.filter(Category.id == category_id)
            products = products.filter(Book.category_id.__eq__(category_id))
            # products = db.session.query()

    if kw:
        products = products.filter(Book.name.contains(kw))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return products.slice(start, end).all()


def count_products(category_id=0, kw=None):
    products = Book.query
    if category_id == None:
        category_id = '0'
      
    if category_id:
        if category_id == str(0):
            products = Book.query
        else:
            products = products.filter(Book.category_id.__eq__(category_id))

    if kw:
        products = products.filter(Book.name.contains(kw))

    return products.count()


def add_comment(content, book_id):
    c = Comment(content=content, book_id=book_id, user=current_user)

    db.session.add(c)
    db.session.commit()
    
    return c


def get_comment(book_id, qttcomment):
    return Comment.query.filter(Comment.book_id.__eq__(book_id) ).order_by(-Comment.id).slice(0, qttcomment).all()


def count_comments(book_id):
    return Comment.query.filter(Comment.book_id.__eq__(book_id)).count()



def get_name_cate(category_id):
    if category_id == None:
        category_id = '0'
    if category_id == str(0):
        return 'All products'
    else:
        return ParentCategory.query.get(category_id)
 


def get_name_category_by_id(category_id):
    return Category.query.get(category_id)



def get_name_parentcategory_by_id(parent_id):
    return ParentCategory.query.get(parent_id)


def product_month_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
                     .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id))\
                     .filter(extract('year', Receipt.created_date) == year)\
                     .group_by(extract('month', Receipt.created_date))\
                     .order_by(extract('month', Receipt.created_date)).all()


def product_month_statss():
    return db.session.query(Category.id, Category.name,func.sum(ReceiptDetail.quantity),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price), Book.id)\
                        .join(Book, Book.category_id.__eq__(Category.id))\
                        .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id))\
                        .group_by(Category.id, Category.name)

                    
def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Book.id, Book.name,
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))\
                  .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id), isouter=True)\
                  .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
                  .group_by(Book.id, Book.name)

    if kw:
        p = p.filter(Book.name.contains(kw))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()











                    
def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Book.id, Book.name,
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))\
                  .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id), isouter=True)\
                  .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
                  .group_by(Book.id, Book.name)

    if kw:
        p = p.filter(Book.name.contains(kw))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()









