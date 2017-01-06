# main.py
# Aritra Biswas, 2016
#
# Main Flask routines for lightcoin.

from __future__ import print_function
import sys

from flask import Flask, render_template, request, redirect, session
from flask.ext.mysql import MySQL

from werkzeug import generate_password_hash, check_password_hash

import time


## INITIALIZATION

app = Flask(__name__)
app.secret_key = '\xee\x81\t3\x1c\x0c\xe6\xbf\x85\xb6F\xfe\x18\x02\xe8\xe0Q8a\xf83\xe8\xbd\xdc'
mysql = MySQL()

# enter MySQL database
app.config['MYSQL_DATABASE_USER'] = 'lightcoin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'lightcoin_key'
app.config['MYSQL_DATABASE_DB'] = 'store'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


## LOGIN AND LOGOUT

@app.route('/')
def main():
    '''Display a login prompt, or redirect to home if user is logged in.'''

    if session.get('user'):
        return redirect('/home')

    return render_template('index.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    '''Validate the user's credentials and redirect them to the lightcoin
    console.'''

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # get password of user
        args = (request.form['username'],)
        cursor.callproc('GetUserPassword', args)
        data = cursor.fetchone()
        
        # validate user
        if data:
            if check_password_hash(data[0], request.form['password']):

                # register session
                session['user'] = request.form['username']
        
                return redirect('/home')

            else:
                return render_template(
                    'error.html',
                    error = 'Wrong password.'
                )
        else:
            return render_template(
                'error.html',
                error = 'Username does not exist.'
            )


        # close connection
        cursor.close()
        conn.close()
        
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    '''Takes the user back to the login screen.'''

    session.pop('user', None)
    return redirect('/')


## HOME SCREEN

@app.route('/home')
def home():
    '''Display some sales statistics.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # get top sellers and top grossing items
    cursor.callproc('GetTopSellers')
    top_sellers = cursor.fetchall()
    cursor.callproc('GetTopGrossing')
    top_grossing = cursor.fetchall()

    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'home.html',
        top_sellers = top_sellers,
        top_grossing = top_grossing,
        user = session.get('user')
    )


## EMPLOYEE/USER MANAGEMENT INTERFACE

@app.route('/employee')
def employee():
    '''List employees and allow adding a new employee.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # fetch employee data
    cursor.callproc('GetEmployees')
    employees = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'employee.html',
        user = session.get('user'),
        employees = employees
    )

@app.route('/employee_add', methods = ['POST'])
def add_employee():
    '''Adds a new employee to the employee table. If username already exists,
    the SQL stored procedure makes no modifications.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # make sure passwords match
        if request.form['password'] != request.form['confirm_password']:
            return render_template(
                'error.html',
                error = 'Passwords did not match.'
            )
            

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # attempt to add employee
        
        args = (
            request.form['username'],
            generate_password_hash(request.form['password']),
            time.strftime('%Y%m%d'),
            request.form['priv']
        )
        cursor.callproc('CreateUser', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/employee')

@app.route('/employee_delete', methods = ['POST'])
def delete_employee():
    '''Deletes an employee from the employee table.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # delete user
        args = (request.form['username'],)
        cursor.callproc('DeleteUser', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/employee')


## PRODUCT MANAGEMENT INTERFACE

@app.route('/product', methods=['POST', 'GET'])
def product():
    '''Display a paginated product list, with options to
    add a new product (new entry in product_line) or a new pack size
    of an existing product.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetProducts', args)
    products = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'product.html',
        user = session.get('user'),
        products = products,
        page = page
    )

@app.route('/product_line_add', methods = ['POST'])
def add_product():
    '''Adds a new product. This corresponds to a new product_line as
    well as a new product associated with that product_line -- both tables
    are updated.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()


        # attempt to add product
        args = (
            request.form['upc'],
            request.form['pid'],
            request.form['name'],
            request.form['pack_size'],
            request.form['cost'],
            request.form['sale']
        )
        cursor.callproc('CreateProduct', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/product')

@app.route('/product_add', methods = ['POST'])
def add_product_pack():
    '''Adds a new pack size of an existing product. Product must already
    exist in product_line.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()


        # attempt to add product
        args = (
            request.form['upc'],
            request.form['pid'],
            request.form['pack_size'],
            request.form['cost'],
            request.form['sale']
        )
        cursor.callproc('CreateProductPack', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/product')

@app.route('/product_delete', methods = ['POST'])
def delete_product_pack():
    '''Delete a product pack. If this is the last pack of this product,
    delete the product as well.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # delete product
        args = (request.form['upc'],)
        cursor.callproc('DeleteProduct', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/product')


## CUSTOMER MANAGEMENT INTERFACE

@app.route('/customer', methods=['POST', 'GET'])
def customer():
    '''Display customer list.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetCustomers', args)
    customers = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'customer.html',
        user = session.get('user'),
        customers = customers,
        page = page
    )

@app.route('/customer_add', methods = ['POST'])
def add_customer():
    '''Add a new customer.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # attempt to add customer
        args = (
            request.form['name'],
            request.form['phone']
        )
        cursor.callproc('CreateCustomer', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/customer')

@app.route('/customer_delete', methods = ['POST'])
def delete_customer():
    '''Delete a customer. TODO: deal with receipts referring to this
    customer.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # delete product
        args = (request.form['cid'],)
        cursor.callproc('DeleteCustomer', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/customer')


## VENDOR MANAGEMENT INTERFACE

@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
    '''Display vendor list.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetVendors', args)
    vendors = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'vendor.html',
        user = session.get('user'),
        vendors = vendors,
        page = page
    )

@app.route('/vendor_add', methods = ['POST'])
def add_vendor():
    '''Add a new vendor.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # attempt to add vendor
        args = (
            request.form['name'],
            request.form['rating']
        )
        cursor.callproc('CreateVendor', args)
        conn.commit()
        
        # close connection
        cursor.close()
        conn.close()

    return redirect('/vendor')

@app.route('/vendor_delete', methods = ['POST'])
def delete_vendor():
    '''Delete a vendor. TODO: deal with orders referring to this
    vendor.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # delete product
        args = (request.form['vid'],)
        cursor.callproc('DeleteVendor', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return redirect('/vendor')


## SALE/ORDER/BREAKAGE INTERFACE

@app.route('/sale_new')
def new_sale():
    return new_transaction('s')

@app.route('/order_new')
def new_order():
    return new_transaction('o')

@app.route('/breakage_new')
def new_breakage():
    return new_transaction('b')

def new_transaction(transaction_type):
    '''Initiate a new transaction and send the user to the transaction page.'''

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # start a transaction and grab its transaction_id
    args = (session.get('user'), transaction_type)
    cursor.callproc('StartTransaction', args)
    transaction_id = cursor.fetchone()[0]
    conn.commit()
        
    # close connection
    cursor.close()
    conn.close()

    return transaction(transaction_id)

def transaction(transaction_id):
    '''List current transaction and allow adding items.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # show this transaction
    args = (transaction_id,)
    cursor.callproc('ViewTransaction', args)
    items = cursor.fetchall()

    # get transaction type
    args = (transaction_id,)
    cursor.callproc('GetTransactionType', args)
    transaction_type = cursor.fetchone()[0]

    # assemble subtotal, tax, total, etc.
    totals = {}

    if transaction_type == 's':
            
        args = (transaction_id,)
        cursor.callproc('CalculateSaleInfo', args)
        subtotal, tax, total = cursor.fetchone()

        totals['subtotal'] = subtotal
        totals['tax'] = tax
        totals['total'] = total

    else:
        
        args = (transaction_id,)
        cursor.callproc('CalculateTransactionTotal', args)
        total = cursor.fetchone()[0]
        
        totals['total'] = total

    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'transaction.html',
        user = session.get('user'),
        tid = transaction_id,
        items = items,
        transaction_type = transaction_type,
        totals = totals
    )

@app.route('/transaction_continue', methods = ['POST'])
def continue_transaction():
    '''Allows finishing an incomplete transaction.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':
        return transaction(int(request.form['tid']))

@app.route('/transaction_add', methods = ['POST'])
def add_to_transaction():
    '''Add an item to a transaction. The SQL stored procedure handles updating
    the quantity or adding a new line_item as needed.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # figure out whether transaction is add or remove
        args = (request.form['tid'],)
        cursor.callproc('GetTransactionType', args)
        transaction_type = cursor.fetchone()[0]
        if transaction_type == 'o':
            add_or_remove = 1
        else:
            add_or_remove = -1

        # add item
        args = (
            request.form['upc'],
            request.form['tid'],
            add_or_remove
        )
        cursor.callproc('AddItemToTransaction', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return transaction(request.form['tid'])

@app.route('/transaction_delete', methods = ['POST'])
def delete_from_transaction():
    '''Removes a line item from a transaction.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # figure out whether transaction is add or remove
        args = (request.form['tid'],)
        cursor.callproc('GetTransactionType', args)
        transaction_type = cursor.fetchone()[0]
        if transaction_type == 'o':
            add_or_remove = 1
        else:
            add_or_remove = -1

        # delete item
        args = (
            request.form['upc'],
            request.form['tid'],
            add_or_remove
        )
        cursor.callproc('DeleteItemFromTransaction', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return transaction(request.form['tid'])

@app.route('/transaction_view', methods = ['POST'])
def view_transaction():
    '''List a previously entered transaction. Only lookups - no computation or
    editability.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # grab transaction ID
    transaction_id = request.form['tid']

    # show this transaction
    args = (transaction_id,)
    cursor.callproc('ViewTransaction', args)
    items = cursor.fetchall()

    # get transaction type
    args = (transaction_id,)
    cursor.callproc('GetTransactionType', args)
    transaction_type = cursor.fetchone()[0]

    # assemble details
    details = {}
    
    if transaction_type == 's':
        
        args = (transaction_id,)
        cursor.callproc('GetSaleDetails', args)
        data = cursor.fetchone()
        payment, total, tax, tender, customer, employee, date_time = data

        details['payment'] = payment
        details['total'] = total
        details['tax'] = tax
        details['subtotal'] = float(total) - float(tax)
        details['tender'] = tender
        details['customer'] = customer
        details['employee'] = employee
        details['date_time'] = date_time

    elif transaction_type == 'o':

        args = (transaction_id,)
        cursor.callproc('GetOrderDetails', args)
        data = cursor.fetchone()
        total, vendor, employee, date_time = data

        details['total'] = total
        details['vendor'] = vendor
        details['employee'] = employee
        details['date_time'] = date_time
    
    elif transaction_type == 'b':

        args = (transaction_id,)
        cursor.callproc('GetBreakageDetails', args)
        data = cursor.fetchone()
        total, employee, date_time = data

        details['total'] = total
        details['employee'] = employee
        details['date_time'] = date_time

    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'transaction_view.html',
        user = session.get('user'),
        tid = transaction_id,
        items = items,
        transaction_type = transaction_type,
        details = details
    )

@app.route('/sale_checkout', methods = ['POST'])
def checkout_sale():
    '''Requests checkout information for a sale.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # grab subtotal and total
        args = (request.form['tid'],)
        cursor.callproc('CalculateSaleInfo', args)
        subtotal, tax, total = cursor.fetchone()

        # grab customers
        args = (
            200, # number of customers to show in dropdown
            0 # start at beginning
        )
        cursor.callproc('GetCustomers', args)
        customers = cursor.fetchall()

        # close connection
        cursor.close()
        conn.close()

    return render_template(
            'sale_checkout.html',
            user = session.get('user'),
            tid = request.form['tid'],
            subtotal = subtotal,
            tax = tax,
            total = total,
            customers = customers
    )

@app.route('/order_checkout', methods = ['POST'])
def checkout_order():
    '''Requests checkout information for an order.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # grab total
        args = (request.form['tid'],)
        cursor.callproc('CalculateTransactionTotal', args)
        total = cursor.fetchone()[0]

        # grab vendors
        args = (
            200, # number of customers to show in dropdown
            0 # start at beginning
        )
        cursor.callproc('GetVendors', args)
        vendors = cursor.fetchall()

        # close connection
        cursor.close()
        conn.close()

    return render_template(
            'order_checkout.html',
            user = session.get('user'),
            tid = request.form['tid'],
            total = total,
            vendors = vendors
    )

@app.route('/sale_finalize', methods = ['POST'])
def finalize_sale():
    '''Records a sale.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()


        # collect and save transaction information
        tid, total, tender = (
            request.form['tid'],
            request.form['total'],
            request.form['tender']
        )
        args = (
            tid,
            total,
            request.form['payment_method'],
            request.form['cid'],
            request.form['tax'],
            tender
        )
        cursor.callproc('FinalizeSale', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return render_template(
        'sale_done.html',
        tid = tid,
        total = total,
        tender = tender,
        change = str(float(tender) - float(total)),
        user = session.get('user')
    )

@app.route('/order_finalize', methods = ['POST'])
def finalize_order():
    '''Records an order.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # collect and save order information
        tid, total = (
            request.form['tid'],
            request.form['total'],
        )
        args = (
            tid,
            total,
            request.form['vid'],
        )
        cursor.callproc('FinalizeOrder', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return render_template(
        'order_done.html',
        tid = tid,
        total = total,
        user = session.get('user')
    )

@app.route('/breakage_finalize', methods = ['POST'])
def finalize_breakage():
    '''Records a breakage.'''

    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    if request.method == 'POST':

        # connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # grab total
        args = (request.form['tid'],)
        cursor.callproc('CalculateTransactionTotal', args)
        total = cursor.fetchone()[0]

        # collect and save transaction information
        tid = request.form['tid']
        args = (
            tid,
            total
        )
        cursor.callproc('FinalizeBreakage', args)
        conn.commit()

        # close connection
        cursor.close()
        conn.close()

    return render_template(
        'breakage_done.html',
        tid = tid,
        total = total,
        user = session.get('user')
    )


## TRANSACTIONS INTERFACE

@app.route('/transaction', methods=['POST', 'GET'])
def list_transaction():
    '''Display transaction list. Transactions cannot be removed
    in the interface.'''
    
    # login-only page
    if not session.get('user'):
        return render_template(
            'error.html',
            error = 'Unauthorized access.'
        )

    # parse page number
    if request.method == 'POST':
        page = int(request.form['page'])
    else:
        page = 0

    # connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # number of items per page
    list_limit = 10

    # fetch product data
    args = (list_limit, page * list_limit)
    cursor.callproc('GetTransactions', args)
    transactions = cursor.fetchall()
        
    # close connection
    cursor.close()
    conn.close()

    return render_template(
        'transaction_list.html',
        user = session.get('user'),
        transactions = transactions,
        page = page
    )


## MAIN

if __name__ == '__main__':
    app.run(debug = True)
