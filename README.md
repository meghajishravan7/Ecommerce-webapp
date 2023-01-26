# Bonsai House

## CS50
>This was my final project to conclude the CS50 Introduction to Computer Sciense course.
>CS, python, flask, flask web framework, web development, CS50, html, css, bootstrap, javascript, mysql
## Features
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)

I've used Flask web framework based in Python
it was necessary to flask for managing SQL database with sqlite3

## Explaining the project and the database
My final project is a website that allow the user register for an online bonsai strore and
get home delivery of plants and tools for gardening purpose. The user can also change his password anytime, send messages to contact the owner and select products for purchasing and get home delivery

All information about users, cases and selected cases for each people are stored in userdata.db.

I used sql extension for connect the database to application and sqlite3 to manager her.

###  sqlite3:
I needed five tables for my database:

- First, table users. Where I put, id, username, hash (for password) and email, notice that id must be a primary key here.

- Second, table transactions. I put id, user_id, address, mobile, description, time, totalprice.  Notice that here user_id must be a foreign key.

- Three, table products, this table is for storing products, prices, description and link for the image

- Four , table messages, this table stores the messages received by the customers to contact the admin

- five , table cart. this stores user_id, product_id, quantity and price of product to show in the cart

### example for handing database in app.py

```python
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
```

another example

```python
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
```

Total code and templates are available above



## About CS50
CS50 is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

Thank you for all CS50.

- Where I get CS50 course?
https://cs50.harvard.edu/x/2020/
