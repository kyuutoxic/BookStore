from flask import render_template, redirect, request, url_for, session, jsonify
from __init__ import app, login
from admin import *
from models import *
from flask_login import login_user, logout_user, login_required
import utils
import cloudinary



@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    user = utils.check_login(username=username,
                            password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.context_processor
def common_response():
    return {
        'categories': utils.read_parent_category(),
        'books': utils.read_books(),
        'cart_stats': utils.cart_stats(session.get('cart'))
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/books/<int:book_id>')
def book_detail(book_id): 
    book = utils.get_book_by_id(book_id=book_id)
    language = utils.get_language_by_id(book.language_id)
    return render_template('book-detail.html', book = book, language=language)


@app.route('/login', methods=["GET", "POST"])
def user_login():
    err_msg = ''
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password', "")

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'index')
            return redirect(url_for(next))
        else:
            err_msg = 'User name or password is not precision'
    return render_template('login.html', err_msg=err_msg)


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

                    utils.add_user(firstname=firstname,lastname=lastname,email=email ,username=username, password=password, avatar=avatar_path)
                    return redirect(url_for('user_login'))
                else:
                    err_msg = 'Mat khau khong khop'
            else:
                err_msg = 'Tai khoan trung'
        except Exception as ex:
            err_msg = 'He thong dang co loi: ' + str(ex)
    
    return render_template('register.html', err_msg=err_msg)


@app.route('/user-logout')
def user_signout():
    logout_user()
    cart = session.get('cart')

    del session['cart']
    return redirect(url_for('user_login'))


@app.route('/cart')
def cart():
    return render_template('cart.html',
                           cart_stats=utils.cart_stats(session.get('cart')))


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


@app.route('/api/pay', methods=['post'])
def pay():
    try:
        utils.add_receipts(session.get('cart'))

        del session['cart']
        return jsonify({'code': 200})
    except Exception as ex:
        print(str(ex))
        return jsonify({'code': 400})



@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')
    if cart:
        if id in cart and quantity:
            cart[id]['quantity'] = quantity
            session['cart'] = cart

    return jsonify(utils.cart_stats(cart))


@app.route('/api/cart/<book_id>', methods=['delete'])
def delete_cart(book_id):
    cart = session.get('cart')
    if cart:
        if book_id in cart:
            del cart[book_id]
            session['cart'] = cart

    return jsonify(utils.cart_stats(cart))


if __name__ == '__main__':
    app.run(debug=True)