from flask import Flask, render_template, redirect, request, url_for, flash
import psycopg2


app = Flask(__name__)

def get_db_connection():
    db = "dbname=rosedb user=ottoagcfg password=dTj*&56$es host=13.228.23.160 port=8432"
    conn = psycopg2.connect(db)
    return conn


@app.route("/")
def main():
    return render_template('login.html')

@app.route("/logout")
def logout():
    return render_template('login.html')

@app.route("/submitlogin", methods=['POST'])
def submitlogin():
    email = request.form.get('email')
    password = request.form['password']
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('select email,password from users where email = %s' , [email])
    except Exception as err:
        return render_template('login.html', error_statement=err)
    
    user = cur.fetchall()
    cur.close()
    conn.close()

    if user[0][1] != password :
        errorStatement = "email or password is incorrect"
        return render_template('login.html', error_statement=errorStatement)
    
    return redirect(url_for('product'))


@app.route("/registerForm")
def registerForm():
    return render_template('registerForm.html')


@app.route("/register", methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']

    if password != confirmPassword :
        errorStatement = "confirm password not match"
        return render_template('registerForm.html', error_statement=errorStatement)
    

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (username, email, password) values (%s,%s,%s);', (username, email, password))
        conn.commit()
    except Exception as err:
        return render_template('registerForm.html', error_statement=err)
    
    cur.close()
    conn.close()
    return redirect(url_for('main'))

@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/product")
def product():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products;')
    
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('product.html' , menu='master', submenu='product', data=products)

@app.route("/addproductForm")
def addproductForm():
    return render_template('addproductForm.html' , menu='master', submenu='product')

@app.route("/addproduct", methods=['POST'])
def addproduct():
    code = request.form.get('code')
    name = request.form.get('name')
    price = request.form.get('price')
    stock = request.form.get('stock')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO products (code, name, price, stock) values (%s,%s,%s,%s);', (code, name, int(price), int(stock)))
        conn.commit()
    except Exception as err:
        return render_template('addproductForm.html', error_statement=err)
    
    cur.close()
    conn.close()
    return redirect(url_for('product'))

@app.route("/supplier")
def supplier():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM suppliers;')
    suppliers = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('supplier.html' , menu='master', submenu='supplier', data=suppliers)

@app.route("/addsupplierForm")
def addsupplierForm():
    return render_template('addsupplierForm.html' , menu='master', submenu='supplier')

@app.route("/addsupplier", methods=['POST'])
def addsupplier():
    code = request.form.get('code')
    name = request.form.get('name')
    address = request.form.get('address')
    telephone = request.form.get('phone')
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO suppliers (code, name, address, telephone) values (%s,%s,%s,%s);', (code, name, address, telephone))
        conn.commit()
    except Exception as err:
        return render_template('addsupplierForm.html', error_statement=err)
    
    cur.close()
    conn.close()
    return redirect(url_for('supplier'))

@app.route("/customer")
def customer():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers;')
    customers = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('customer.html' , menu='master', submenu='customer', data=customers)

@app.route("/addcustomerForm")
def addcustomerForm():
    return render_template('addcustomerForm.html' , menu='master', submenu='customer')


@app.route("/addcustomer", methods=['POST'])
def addcustomer():
    code = request.form['code']
    name = request.form['name']
    address = request.form['address']
    telephone = request.form['phone']
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('INSERT INTO customers (code, name, address, telephone) values (%s,%s,%s,%s);', (code, name, address, telephone))
        conn.commit()
    except Exception as err:
        return render_template('addcustomerForm.html', error_statement=err)
    
    cur.close()
    conn.close()
    return redirect(url_for('customer'))

@app.route("/purchaseForm")
def purchaseForm():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM suppliers;')
    suppliers = cur.fetchall()
    cur.execute('SELECT * FROM products;')
    products = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('purchaseForm.html' , menu='purchase', submenu='form', data_supplier=suppliers , data_product=products)

@app.route("/addpurchase", methods=['POST'])
def addpurchase():
    supplier_code = request.form.get('supplier_code')
    product_code = request.form.get('product_code')
    quantity = request.form.get('quantity')
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO purchase (supplier_code, product_code, quantity) values (%s,%s,%s);', (supplier_code, product_code, int(quantity)))
        cur.execute('SELECT stock from products where code = %s', [product_code])
        product = cur.fetchall()
        stock = product[0][0] + int(quantity)
        cur.execute('update products set stock = %s where code = %s', (stock, product_code))
        conn.commit()
    except Exception as err:
        conn.rollback()
        return render_template('purchaseForm.html', error_statement=err)
    
    
    cur.close()
    conn.close()
    return redirect(url_for('purchaseReport'))

@app.route("/purchaseReport")
def purchaseReport():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT p.supplier_code, s.name, p.product_code, pts.name, p.quantity FROM purchase p left join suppliers s on s.code = p.supplier_code left join products pts on pts.code = p.product_code order by p.id desc;')
    purchase = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('purchaseReport.html' , menu='purchase', submenu='report', data=purchase)

@app.route("/salesForm")
def salesForm():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers;')
    customers = cur.fetchall()
    cur.execute('SELECT * FROM products;')
    products = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('salesForm.html' , menu='sales', submenu='form', data_customer=customers , data_product=products)

@app.route("/addsales", methods=['POST'])
def addsales():
    customer_code = request.form.get('customer_code')
    product_code = request.form.get('product_code')
    quantity = request.form.get('quantity')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT price, stock FROM products where code = %s;', [product_code])
    product = cur.fetchall()
    if product[0][1] < int(quantity):
        return render_template('salesForm.html', error_statement="not enough stock")

    total = product[0][0] * int(quantity)
    try:
        cur.execute('INSERT INTO sales (customer_code, product_code, quantity, total_price) values (%s,%s,%s,%s);', (customer_code, product_code, int(quantity), total))
        cur.execute('SELECT stock from products where code = %s', [product_code])
        product = cur.fetchall()
        stock = product[0][0] - int(quantity)
        cur.execute('update products set stock = %s where code = %s', (stock, product_code))
        conn.commit()
    except Exception as err:
        return render_template('salesForm.html', error_statement=err)
    
    cur.close()
    conn.close()
    return redirect(url_for('salesReport'))

@app.route("/salesReport")
def salesReport():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT s.customer_code, c.name, s.product_code, pts.name, pts.price, s.quantity , s.total_price FROM sales s left join customers c on c.code = s.customer_code left join products pts on pts.code = s.product_code order by s.id desc;')
    sales = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('salesReport.html' , menu='sales', submenu='report', data=sales)




if __name__ == "__main__":
    app.run(debug=True)