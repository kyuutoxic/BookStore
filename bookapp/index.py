from flask import render_template, redirect, request, url_for, session, jsonify
from __init__ import app, login
from admin import *
from models import *
from flask_login import login_user, logout_user, login_required
import utils
import cloudinary
import math



@app.context_processor
def common_response():
    return {
        'categories': utils.read_parent_category(),
        'books': utils.read_books(),
        'cart_stats': utils.cart_stats(session.get('cart'))
    }


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



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/products")
def product_list():
    category_id = request.args.get('category_id')
    kw = request.args.get('kw')
    page = request.args.get('page', 1, type=int)

    products = utils.load_products(category_id=category_id,kw=kw,page=page)
    counter = utils.count_products(category_id=category_id,kw=kw)


    return render_template('products.html',
                           products=products, pages=math.ceil(counter/app.config['PAGE_SIZE']), page=page, name_cate=utils.get_name_cate(category_id=category_id))
                           


@app.route('/books/<int:book_id>')
def book_detail(book_id): 
    book = utils.get_book_by_id(book_id=book_id)
    language = utils.get_language_by_id(book.language_id)
    cate_name = utils.get_name_category_by_id(book.category_id)
    parent_name = utils.get_name_parentcategory_by_id(cate_name.parent_id)
    counter = utils.count_comments(book_id=book_id)
    return render_template('book-detail.html', book = book, language=language, counter=counter, cate_name=cate_name,parent_name=parent_name)



@app.route('/login', methods=["GET", "POST"])
def user_login():
    err_msg = ''
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password', "")

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)

            if 'book_id' in  request.args:
                return redirect(url_for(request.args.get('next', 'index'), book_id=request.args['book_id']))
                
            return redirect(url_for(request.args.get('next', 'index')))
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
    if cart:
        del session['cart']
    return redirect(url_for('index'))


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


@app.route('/api/minicart/<book_id>', methods=['delete'])
def delete_mini_cart(book_id):
    cart = session.get('cart')
    if cart:
        if book_id in cart:
            del cart[book_id]
            session['cart'] = cart

    return jsonify(utils.cart_stats(cart))


@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    book_id = data.get('book_id')

    try:
        c = utils.add_comment(content=content, book_id=book_id)

        return jsonify({
            "status":200,
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
        return jsonify({"status":404})


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


@app.route('/checkout',methods=['get', 'post'])
@login_required
def checkout():
    city = utils.load_city()

    if request.method.__eq__('POST'):

        cus_name = request.form['name']
        phone_number = request.form['number']
        city_id = request.form['country_name']
        district_id = request.form['district_name']
        street_name = request.form['address']
        opt = request.form['opt']

        if street_name and district_id and city_id:
            address_id = utils.get_address(street_name=street_name, district_id=district_id, city_id=city_id)
            if address_id != 0:
                utils.add_receipts(session.get('cart'), cus_name=cus_name, phone_number=phone_number, opt=opt, address_id=address_id)
            else:
                address = utils.add_address(street_name=street_name, district_id=district_id, city_id=city_id)
                utils.add_receipts(session.get('cart'), cus_name=cus_name, phone_number=phone_number, opt=opt, address_id=address.id)

            cart = session.get('cart')
            if cart:
                del session['cart']
            return redirect(url_for('index'))

    return render_template('checkout.html', city=city)


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

@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__ == '__main__':
    app.run(debug=True)