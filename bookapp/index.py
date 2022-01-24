from hashlib import new
from re import T
from flask import render_template, redirect, request, url_for, session, jsonify
from __init__ import app, login
from admin import *
from models import *
from flask_login import login_user, logout_user, login_required
import utils
from utils import read_receiptdetails_by_receipt_id, get_book_by_id
import cloudinary
import math
import smtplib
import cloudinary.uploader
import json
import urllib.request
import uuid
import hmac
import hashlib
import MoMo


# Dữ liệu sài chung
@app.context_processor
def common_response():
    return {
        'categories': utils.read_parent_category(),
        'books': utils.read_books(),
        'cart_stats': utils.cart_stats(session.get('cart'))
    }



# Đặng nhập Admin
@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    user = utils.check_login(username=username,
                             password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


# Log user
@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")


# Trang sản phản
@app.route("/products")
def product_list():
    category_id = request.args.get('category_id')
    kw = request.args.get('kw')
    page = request.args.get('page', 1, type=int)

    products = utils.load_products(category_id=category_id, kw=kw, page=page)
    counter = utils.count_products(category_id=category_id, kw=kw)

    return render_template('products.html',
                           products=products, pages=math.ceil(counter/app.config['PAGE_SIZE']), page=page, name_cate=utils.get_name_cate(category_id=category_id))


# Trang chi tiết sản phẩm
@app.route('/books/<int:book_id>')
def book_detail(book_id):
    book = utils.get_book_by_id(book_id=book_id)
    language = utils.get_language_by_id(book.language_id)
    cate_name = utils.get_name_category_by_id(book.category_id)
    parent_name = utils.get_name_parentcategory_by_id(cate_name.parent_id)
    counter = utils.count_comments(book_id=book_id)
    return render_template('book-detail.html', book=book, language=language, counter=counter, cate_name=cate_name, parent_name=parent_name)


# Đăng nhập Client
@app.route('/login', methods=["GET", "POST"])
def user_login():
    err_msg = ''
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password', "")

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)

            if 'book_id' in request.args:
                return redirect(url_for(request.args.get('next', 'index'), book_id=request.args['book_id']))

            return redirect(url_for(request.args.get('next', 'index')))
        else:
            err_msg = 'User name or password is not precision'
    return render_template('login.html', err_msg=err_msg)


# Đăng kí
@app.route('/register', methods=["get", "post"])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('passwordConfirm')
        avatar_path = None

        try:
            if utils.check_username(username) == True:
                if password.strip().__eq__(confirm.strip()):
                    avatar = request.files.get('avatar')
                    if avatar:
                        res = cloudinary.uploader.upload(avatar)
                        avatar_path = res['secure_url']

                    utils.add_user(firstname=firstname, lastname=lastname, email=email,
                                   username=username, password=password, avatar=avatar_path)
                    return redirect(url_for('user_login'))
                else:
                    err_msg = 'Confirm password does not match'
            else:
                err_msg = 'Username has exist'
        except Exception as ex:
            err_msg = 'Error system: ' + str(ex)

    return render_template('register.html', err_msg=err_msg)


# Đăng xuất
@app.route('/user-logout')
def user_signout():
    logout_user()
    cart = session.get('cart')
    if cart:
        del session['cart']
    return redirect(url_for('index'))


# Trang giỏ hàng
@app.route('/cart')
def cart():

    return render_template('cart.html',
                           cart_stats=utils.cart_stats(session.get('cart')))


# API giỏ hàng
@app.route('/api/add-to-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')
    image = data.get('image')

    cart = session.get('cart')
    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'image': image,
            'quantity': 1
        }

    session['cart'] = cart

    return jsonify(utils.cart_stats(session.get('cart')))


# API giỏ hàng MINI
@app.route('/api/add-to-cart/minicart', methods=['post'])
def add_to_minicart():

    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')
    image = data.get('image')

    cart = session.get('cart')
    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'image': image,
            'quantity': 1
        }

    session['cart'] = cart
    results = session['cart']

    return jsonify(results)


# API thanh toán
@app.route('/api/pay', methods=['post'])
def pay():
    try:
        utils.add_receipts(session.get('cart'))

        del session['cart']
        return jsonify({'code': 200})
    except Exception as ex:
        print(str(ex))
        return jsonify({'code': 400})


# API cập nhật giỏ hàng
@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')
    book = utils.get_book_by_id(book_id=id)

    if utils.check_stock(book_id=id, quantity=quantity) == True:
        cart = session.get('cart')
        if cart:
            if id in cart and quantity:
                cart[id]['quantity'] = quantity
                session['cart'] = cart
            data = utils.cart_stats(cart)

        return jsonify({
            "status": 200,
            'data': data
        })
    else:
        return jsonify({
            "status": 404,
            'data': {
                'id': id,
                'quantity': book.quantity
            }
        })


# API xóa sản phẩm trong giỏ hàng
@app.route('/api/cart/<book_id>', methods=['delete'])
def delete_cart(book_id):
    cart = session.get('cart')
    if cart:
        if book_id in cart:
            del cart[book_id]
            session['cart'] = cart

    return jsonify(utils.cart_stats(cart))


# APi xóa sản phẩm trong giỏ hàng MINI
@app.route('/api/minicart/<book_id>', methods=['delete'])
def delete_mini_cart(book_id):
    cart = session.get('cart')
    if cart:
        if book_id in cart:
            del cart[book_id]
            session['cart'] = cart

    return jsonify(utils.cart_stats(cart))


# API bình luận
@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    book_id = data.get('book_id')

    try:
        c = utils.add_comment(content=content, book_id=book_id)

        return jsonify({
            "status": 200,
            "data": {
                "id": c.id,
                "content": c.content,
                'created_date': str(c.created_date),
                'user': {
                    'id': c.user.id,
                    'username': c.user.username,
                    'avatar': c.user.avatar
                }
            }
        })
    except:
        return jsonify({"status": 404})


# API xem số lượng bình luận
@app.route('/api/books/<int:book_id>/comments/<int:qttcomment>')
def get_comments(book_id, qttcomment):
    comments = utils.get_comment(book_id=book_id, qttcomment=qttcomment)
    results = []
    for c in comments:
        results.append({
            'id': c.id,
            'content': c.content,
            'created_date': str(c.created_date),
            'user': {
                'id': c.user.id,
                'username': c.user.username,
                'avatar': c.user.avatar
            }
        })

    return jsonify(results)


# Trang thanh toán
@app.route('/checkout', methods=['get', 'post'])
@login_required
def checkout():
    city = utils.load_city()

    current_id = session.get('current_id')
    if not current_id:
        current_id = current_user.id
    else:
        current_id = current_user.id
    session['current_id'] = current_id
    if request.method.__eq__('POST'):
        cus_name = request.form['name']
        phone_number = request.form['number']
        city_id = request.form['country_name']
        district_id = request.form['district_name']
        street_name = request.form['address']
        opt = request.form['opt']
        cart = session.get('cart')
        total = utils.cart_stats(cart)['total_amount']
        if opt == "offline":
            r = utils.add_receipts(session.get(
                'cart'), cus_name=cus_name, phone_number=phone_number, opt=opt, address_id=None)
            utils.send_email(info=r)
            if cart:
                del session['cart']
            return redirect(url_for('index'))
        else:
            if street_name and district_id and city_id:
                address_id = utils.get_address(
                    street_name=street_name, district_id=district_id, city_id=city_id)
                if address_id != 0:
                    r = utils.add_receipts(session.get(
                    'cart'), cus_name=cus_name, phone_number=phone_number, opt=opt, address_id=address_id)
                    a = MoMo.momo(total)
                    check_string = a['requestId'] + a['amount'] + a['orderInfo'] + a['orderId'] + a['partnerCode']
                    check_str = session.get('check_str')
                    if not check_str:
                        check_str = check_string
                    else:
                        check_str = check_string
                    session['check_str'] = check_str
                    return redirect(a['payUrl'])
                else:
                    address = utils.add_address(
                        street_name=street_name, district_id=district_id, city_id=city_id)
                    r = utils.add_receipts(session.get(
                    'cart'), cus_name=cus_name, phone_number=phone_number, opt=opt, address_id=address.id)
                    a = MoMo.momo(total)
                    check_string = a['requestId'] + a['amount'] + a['orderInfo'] + a['orderId'] + a['partnerCode']
                    check_str = session.get('check_str')
                    if not check_str:
                        check_str = check_string
                    else:
                        check_str = check_string
                    session['check_str'] = check_str
                    return redirect(a['payUrl'])

    return render_template('checkout.html', city=city)


# API địa chỉ
@app.route('/api/load-address/<int:city_id>')
def load_address(city_id):
    district = utils.load_district_by_city_id(city_id=city_id)
    results = []

    for d in district:
        results.append({
            'id': d.id,
            'name': d.name,
            'city_id': d.city_id
        })

    return jsonify(results)


# Trang Blog
@app.route('/blog')
def blog():
    return render_template('blog.html')


# Trang chi tiết khách hàng
@app.route('/user-detail', methods=['get', 'post'])
def user_detail():
    err_msg = ""

    if request.method.__eq__('POST'):

        id = request.form['id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        if id and first_name and last_name:
            utils.user_update(id=id, first_name=first_name,
                              last_name=last_name, email=email)

    return render_template('user-detail.html', err_msg=err_msg)


# Trang đổi password
@app.route('/change-password', methods=['get', 'post'])
def change_password():
    err_msg = ""
    if request.method.__eq__('POST'):

        id = request.form['id']
        current_password = request.form['CurrentPassword']
        new_password = request.form['NewPassword']
        confirm_password = request.form['ConfirmPassword']
        try:
            if current_password and new_password and confirm_password:
                if utils.check_password(id=id, password=current_password) == True:
                    if new_password == confirm_password:
                        utils.user_password_update(
                            id=id, password=new_password)
                        err_msg = 'Successful'
                        return redirect(url_for('user_detail'))
                    else:
                        err_msg = 'Confirm password does not match'
                else:
                    err_msg = 'Current password does not match'
        except Exception as ex:
            err_msg = 'Error' + str(ex)

    return render_template('changepassword.html', err_msg=err_msg)


# Trang đổi avatar
@app.route('/change-avatar', methods=['get', 'post'])
def change_avatar():
    err_msg = ""
    if request.method.__eq__('POST'):

        id = request.form['id']
        avatar = request.files.get('avatar')
        avatar_path = None
        try:
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
                utils.change_avatar(id=id, avatar=avatar_path)
                err_msg = 'Successful'
                return redirect(url_for('user_detail'))

        except Exception as ex:
            err_msg = 'Error ' + str(ex)

    return render_template('change-avatar.html', err_msg=err_msg)


@app.route('/returnmomo')
def returnmomo():
    notimomo()
    msg = ""
    check_str = session.get('check_str')
    check_string = request.args.get('requestId') + request.args.get('amount') + request.args.get('orderInfo') + request.args.get('orderId') + request.args.get('partnerCode')
    if  (check_str != check_string):
        msg = "Request không hợp lệ!!"
    elif (request.args.get('resultCode')!="0"):
        msg = "Thanh toán thất bại!"
    else:
        msg = "Thanh toán thành công!!"
    return render_template('returnmomo.html', msg=msg)

@app.route('/notimomo')
def notimomo():
    r = utils.get_receipt_by_active_and_id_user(int(session.get('current_id')))
    check_str = session.get('check_str')
    check_string = request.args.get('requestId') + request.args.get('amount') + request.args.get('orderInfo') + request.args.get('orderId') + request.args.get('partnerCode')
    if(request.args.get('resultCode')!="0" or check_str != check_string):
        for i in r:
            if(utils.get_receipt_by_id(i).active == 2):
                utils.del_receipt(i.id)
    elif(check_str == check_string and request.args.get('resultCode')=="0"):
        for i in r:
            if(utils.get_receipt_by_id(i).active == 2):
                utils.change_active_true_by_receipt_id(i)
                utils.send_email(info=utils.get_receipt_by_id(i))
                del session['cart']
    return render_template('notimomo.html')
        


if __name__ == '__main__':
    app.run(debug=True)