import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, success

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

db = SQL('sqlite:///userdata.db')


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
@login_required
def history():
    orders = db.execute('select * from transactions where user_id = ? order by time desc', session['user_id'])
    return render_template('history.html', orders = orders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':

        if not request.form.get('username'):
            return apology('Please provide Username')

        if not request.form.get('password'):
            return apology('Please provide password')

        rows = db.execute('select * from users where username = ?',
                          request.form.get('username'))

        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get('password')):
            return apology('Invalid Username or password, Try again')

        session['user_id'] = rows[0]['id']

        return redirect('/')

    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()

    return redirect('/login')


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    products = db.execute('select * from products')
    return render_template('shop.html', products=products)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')
        name = request.form.get('name')
        email = request.form.get('email')

        if not username:
            return apology("Must Provide Username")
        elif not password:
            return apology("Must type your password")
        elif not confirmation:
            return apology("Must type your confirmation password")
        elif not name:
            return apology('Must provide name')
        elif not email:
            return apology('Must provide email id')

        if password != confirmation:
            return apology("confirmation password doesn't match")

        hash = generate_password_hash(password)

        try:
            db.execute('insert into users (username,hash,name,email) values(?,?,?,?)',
                       username, hash, name, email)
            return success('Success! you are registered, please log in')
        except:
            return apology('Username already exists,try new username')

    else:
        return render_template('register.html')


@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    if request.method == 'POST':
        name = request.form.get('name')
        about = request.form.get('about')
        imglink = request.form.get('imglink')
        type = request.form.get('type')

        try:
            price = int(request.form.get('price'))
        except:
            return apology('price must be integer')

        if price <= 0:
            return apology('price must be positive integer')

        db.execute('insert into products (name, about, price, imglink, type) values(?,?,?,?,?)',
                   name, about, price, imglink, type)

        return redirect('/addproduct')
    else:
        return render_template('addproduct.html')


@app.route('/removeproduct', methods=['GET', 'POST'])
@login_required
def removeproduct():
    if request.method=='POST':
        product_id = request.form.get('product_id')

        if not product_id:
            return apology('Enter product id')

        db.execute('delete from products where id=?', product_id)
        return success('product removed')

    else:
        products = db.execute('select * from products')
        return render_template('removeproduct.html', products=products)

@app.route('/cart', methods=['GET','POST'])
@login_required
def cart():
    if request.method=='POST':
        product_id = request.form.get('product_id')
        quan = request.form.get('quantity')

        if not quan:
            quan=1

        product = db.execute('select quantity from cart where user_id=? and product_id=?', session['user_id'], product_id)
        if product:
            x = int(product[0]['quantity']) + int(quan)
            db.execute('update cart set quantity=? where user_id=? and product_id=?', x, session['user_id'], product_id)
        else:
            db.execute('insert into cart (user_id,product_id,quantity) values(?,?,?)', session['user_id'], product_id, quan)
        flash('product added to cart')
        return redirect('/shop')
    else:
        products = db.execute('select * from cart join products on cart.product_id = products.id where user_id=?', session['user_id'])
        total=0
        for product in products:
            total+= product['quantity']*product['price']
        return render_template('cart.html', products = products, total = total)


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    if request.method == 'POST':
        old = request.form.get('oldpassword')
        new = request.form.get('newpassword')
        newconfirm = request.form.get('newconfirmation')

        if not old or not new or not newconfirm:
            return apology('Must type all the fields')

        if new != newconfirm:
            return apology("new confirmation password doesn't match")

        rows = db.execute('select * from users where id=?', session['user_id'])

        if not check_password_hash(rows[0]['hash'], old):
            return apology('your current password is incorrect')

        hash = generate_password_hash(new)
        db.execute('update users set hash = ? where id=?',
                   hash, session['user_id'])

        return success('Password changed successfully')

    else:
        return render_template('changepassword.html')


@app.route('/bonsai')
def bonsai():
    return render_template('bonsai.html')


@app.route('/about')
def about():
    return render_template('AboutUs.html')


@app.route('/faq')
def faq():
    return render_template('FAQ.html')


@app.route('/contactus', methods=['GET', 'POST'])
@login_required
def contactus():
    if request.method == 'POST':

        msg = request.form.get('message')
        email = request.form.get('email')

        if not msg or not email:
            return apology('Must type all fields')

        db.execute('insert into messages (user_id, email, message) values(?,?,?)',
                   session['user_id'], email, msg)
        return success('Your message has been sent to admin, we will get back to you soon')

    else:
        return render_template('contactus.html')


@app.route('/messages')
@login_required
def messages():
    messages = db.execute('select * from messages order by time desc')
    return render_template('messages.html', messages=messages)


@app.route('/deletecart',methods = ['POST'])
@login_required
def deletecart():
    db.execute('delete from cart where user_id=?',session['user_id'])
    return redirect('/cart')


@app.route('/checkout',methods = ['GET','POST'])
@login_required
def checkout():
    if request.method=='POST':
        products = db.execute('select * from cart join products on cart.product_id = products.id where user_id=?', session['user_id'])
        total=0
        for product in products:
            total+= product['quantity']*product['price']

        if total ==0:
            return apology('no items in cart')

        mobile = request.form.get('mobile')
        address = request.form.get('address')

        if not mobile or not address:
            return apology('please enter all fields')

        db.execute('insert into transactions (user_id,mobile,address,total) values(?,?,?,?)', session['user_id'], mobile, address, total)
        db.execute('delete from cart where user_id=?',session['user_id'])

        return success('Your order has been successfully placed')

    else:
        products = db.execute('select * from cart join products on cart.product_id = products.id where user_id=?', session['user_id'])
        total=0
        for product in products:
            total+= product['quantity']*product['price']
        return render_template('checkout.html', products = products, total = total)