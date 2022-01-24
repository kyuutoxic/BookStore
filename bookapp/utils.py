from models import User
from flask import request, session
import hashlib
from models import Category, Book, ParentCategory, Import, Receipt, ReceiptDetail, Rule, BookLanguage, Comment, City, District, Address, UserRole
from sqlalchemy import func
from __init__ import db, app
from flask_login import current_user
from sqlalchemy.sql import extract
import datetime
import smtplib


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(
            password.strip().encode("utf-8")).hexdigest())

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
        books = books.filter(Book.name.contains(kw.strip()))

    return books.all()


def read_book_from_import():
    return db.session.query(Book.name, Category.name, Book.author, Import.quantities, Import.update_date)\
        .join(Book, Book.id.__eq__(Import.book_id))\
        .join(Category, Category.id.__eq__(Book.category_id))\
        .order_by(-Import.id)\
        .all()


def get_book(book_id):
    return Book.query.get(book_id)


def add_import(book_id, quantities):
    imports = Import(book_id=book_id, quantities=quantities)
    db.session.add(imports)
    db.session.commit()


def get_rule(rule_id):
    return Rule.query.get(rule_id)


def add_receipt(user_id, cus_name=None):
    receipt = Receipt(user_id=user_id, cus_name=cus_name)
    db.session.add(receipt)
    db.session.commit()


def read_receipt_by_active():
    return db.session.query(Receipt.id)\
        .filter(Receipt.active == 0).all()

def get_receipt_by_active_and_id_user(id):
    return db.session.query(Receipt.id)\
        .filter(Receipt.active.__eq__(2) and Receipt.user_id.__eq__(id)).all()

def change_active_true_by_receipt_id(id):
    a = Receipt.query.get(id)
    a.active = 1
    db.session.commit()


def add_receiptdetails(receipt_id, book_id, quantity, unit_price):
    receipt_details = ReceiptDetail(
        receipt_id=receipt_id, book_id=book_id, quantity=quantity, unit_price=unit_price)
    db.session.add(receipt_details)
    db.session.commit()


def update_quantity_receipt_details(receipt_detail_id, quantity):
    a = get_receiptdetails_by_id(receipt_detail_id)
    a.quantity = a.quantity + quantity
    db.session.commit()


def get_receiptdetails_by_id(receipt_detail_id):
    return ReceiptDetail.query.get(receipt_detail_id)


def read_receiptdetails_by_receipt_id(receipt_id):
    return ReceiptDetail.query.filter(ReceiptDetail.receipt_id == receipt_id).all()


def count_receipt():
    return Receipt.query.count()


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


def check_stock(book_id, quantity):
    book = Book.query.get(book_id)
    if book.quantity >= quantity:
        return True
    return False


def read_parent_category():
    return ParentCategory.query.all()


def read_books():
    return Book.query.all()


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def get_language_by_id(language_id):
    return BookLanguage.query.get(language_id)


def check_login(username, password):
    if username and password:
        password = str(hashlib.md5(
            password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()


def check_username(username):
    user = User.query.all()
    for u in user:
        if u.username == username:
            return False
    return True


def add_user(firstname, lastname, email, username, password, **kwargs):
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


def add_receipts(cart, cus_name=None, phone_number=None, address_id=None, opt='offline'):
    if cart:
        if opt == 'offline':

            receipt = Receipt(user=current_user, cus_name=cus_name,
                              phone_number=phone_number, address_id=address_id)
            db.session.add(receipt)
            db.session.commit()

            for c in cart.values():
                detail = ReceiptDetail(receipt_id=receipt.id,
                                       book_id=c['id'],
                                       quantity=c['quantity'], unit_price=c['price'])
                db.session.add(detail)
        else:
            receipt = Receipt(user=current_user, cus_name=cus_name,
                              phone_number=phone_number, address_id=address_id, active=2)
            db.session.add(receipt)
            db.session.commit()
            for c in cart.values():
                detail = ReceiptDetail(receipt_id=receipt.id,
                                       book_id=c['id'],
                                       quantity=c['quantity'], unit_price=c['price'])
                db.session.add(detail)
            receipt_detail_for_update_stock = read_receiptdetails_by_receipt_id(
                receipt_id=receipt.id)
            for b in receipt_detail_for_update_stock:
                update_stock(book_id=b.book_id, quantity=b.quantity)

        db.session.commit()
    return receipt


def load_products(category_id=None, kw=None, page=1):
    products = Book.query

    if category_id == None:
        category_id = '0'

    if category_id:
        if category_id == str(0):
            products = Book.query
        else:
            products = db.session.query(Book).join(Category).filter(
                Category.parent_id.__eq__(category_id))
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
            products = Book.query.filter(
                Category.parent_id.__eq__(category_id))

    if kw:
        products = products.filter(Book.name.contains(kw))

    return products.count()


def add_comment(content, book_id):
    c = Comment(content=content, book_id=book_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comment(book_id, qttcomment):
    return Comment.query.filter(Comment.book_id.__eq__(book_id)).order_by(-Comment.id).slice(0, qttcomment).all()


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


def product_year_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
        .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id))\
        .filter(extract('year', Receipt.created_date) == year)\
        .group_by(extract('month', Receipt.created_date))\
        .order_by(extract('month', Receipt.created_date)).all()


def category_month_stats(month):
    return db.session.query(Category.id, Category.name, func.sum(ReceiptDetail.quantity),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
        .join(Book, Book.category_id.__eq__(Category.id))\
        .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id))\
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
        .filter(extract('month', Receipt.created_date) == month, Receipt.active == 1)\
        .group_by(Category.id, Category.name).all()


def product_month_stats(month):
    return db.session.query(Book.id, Book.name, func.sum(ReceiptDetail.quantity),
                            func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
        .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id))\
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
        .filter(extract('month', Receipt.created_date) == month, Receipt.active == 1)\
        .group_by(Book.id, Book.name).all()


def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Book.id, Book.name,
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price))\
        .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id), isouter=True)\
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
        .group_by(Book.id, Book.name)

    if kw:
        p = p.filter(Book.name.contains(kw.strip()))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def load_city():
    return City.query.all()


def load_district_by_city_id(city_id):
    return District.query.filter(District.city_id.__eq__(city_id))


def add_address(street_name, city_id, district_id):
    address = Address(street_name=street_name,
                      city_id=city_id, district_id=district_id)
    db.session.add(address)
    db.session.commit()

    return address


def get_address(street_name, city_id, district_id):
    a = Address.query
    for i in a:
        if i.street_name.__eq__(street_name) and i.city_id.__eq__(city_id) and i.district_id.__eq__(district_id):
            return i.id
    else:
        return 0


def del_receipt(receipt_id):
    receipt_detail = read_receiptdetails_by_receipt_id(receipt_id=receipt_id)
    for r in receipt_detail:
        del_receipt_detail(r.id)
    Receipt.query.filter(Receipt.id == receipt_id).delete()
    db.session.commit()


def del_receipt_by_rule(time):
    receipts = Receipt.query.filter(Receipt.active == False).all()
    for r in receipts:
        if(datetime.datetime.now() > (r.created_date + datetime.timedelta(hours=time.value))):
            del_receipt(receipt_id=r.id)


def send_email(info):
    EMAIL_ADDRESS = '1951052195thong@ou.edu.vn'
    EMAIL_PASSWORD = 'Trongthung016294600911'
    EMAIL_TO = str(current_user.email)
    rs = read_receiptdetails_by_receipt_id(info.id)
    subject = 'THANK YOU FOR SHOPPING WITH US'
    head = 'Your payment was successfully!\n\nYour receipt ID:' + str(info.id)
    body = '\n\n'
    total = cart_stats(session.get('cart'))['total_amount']
    for i in rs:
        body = body + str(i.quantity) + ' "' + get_book_by_id(i.book_id).name + \
            '" ' + str("{:,.0f}".format(i.unit_price)) + '/unit \n\n'

    if info.active == True:
        footer = 'Total price: ' + \
            str("{:,.0f}".format(total)) + \
            ' VND \n\nThe package will come after a few day, hope you happy!'
    else:
        footer = 'Total price: ' + str("{:,.0f}".format(
            total)) + ' VND \n\nPlease show to the seller your receipt ID when you coming the bookstore within 48 hours, hope you happy!'

    msg = f'Subject: {subject}\n\n{head}\n\n{body}\n{footer}'
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        smtp.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.encode('utf-8'))

        smtp.quit()


def user_update(id, first_name, last_name, email):
    user = User.query.get(id)

    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    db.session.commit()


def check_password(id, password):
    user = User.query.get(id)
    currentpassword = str(hashlib.md5(
        password.strip().encode("utf-8")).hexdigest())
    if user.password == currentpassword:
        return True
    return False


def user_password_update(id, password):
    user = User.query.get(id)
    newpassword = str(hashlib.md5(
        password.strip().encode("utf-8")).hexdigest())

    user.password = newpassword
    db.session.commit()


def change_avatar(id, avatar):
    user = User.query.get(id)

    user.avatar = avatar
    db.session.commit()


def count_cus():
    return User.query.filter(User.role == UserRole.CUSTOMER).count()

if __name__ == '__main__':
    r = get_receipt_by_active_and_id_user(10)
    for i in r:
            if(get_receipt_by_id(i).active == 2):
                change_active_true_by_receipt_id(i.id)