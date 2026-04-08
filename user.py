import mysql.connector
from flask import flash, render_template,request,redirect,url_for,session

con = mysql.connector.connect(host="localhost",user="root",password="captain07",database="busticketdb")

def homepage():
    sql = "select * from category"
    cursor = con.cursor()
    cursor.execute(sql)
    cats = cursor.fetchall()

    # 
    sql = """
    SELECT t.tid, t.tname, t.price, t.destination, t.image_url,
           t.catid, t.tdate, t.ttime, c.catname, t.source
    FROM ticket t
    JOIN category c ON t.catid = c.catid
    """
    cursor = con.cursor()
    cursor.execute(sql)
    tics = cursor.fetchall()

    return render_template("homepage.html",cats=cats,tics=tics)

def ViewTickets(catid):
    sql = "select * from category"
    cursor = con.cursor()
    cursor.execute(sql)
    cats = cursor.fetchall()

    sql = "select catname from category where catid=%s"
    val = (catid,)
    cursor = con.cursor()
    cursor.execute(sql,val)
    category_name = cursor.fetchone()[0]



    # sql = "select * from ticket where catid=%s"
    sql = """
                select t.tid, t.tname, t.price, t.destination, t.image_url,
                    t.catid, t.tdate, t.ttime, c.catname, t.source
                FROM ticket t
                JOIN category c ON t.catid = c.catid
                WHERE c.catid = %s
            """
    val = (catid,)
    cursor = con.cursor()
    cursor.execute(sql,val)
    tics = cursor.fetchall()

    return render_template("homepage.html",cats=cats,tics=tics,category_name=category_name)

def viewDetails(tid):
    if request.method == "GET":
        sql = "select * from category"
        cursor = con.cursor()
        cursor.execute(sql)
        cats = cursor.fetchall()

        # sql = "select * from ticket where tid=%s"
        sql = """
                select t.tid, t.tname, t.price, t.destination, t.image_url,
                    t.catid, t.tdate, t.ttime, c.catname, t.source
                FROM ticket t
                JOIN category c ON t.catid = c.catid
                WHERE t.tid = %s
            """
        val = (tid,)
        cursor = con.cursor()
        cursor.execute(sql,val)
        tic = cursor.fetchone()
        return render_template("viewDetails.html",cats=cats,tic=tic)
    else:
        if "user_name" not in session:
            return redirect(url_for("login"))
        else:
            # Proceed to buy
            qty = request.form["qty"]
            username = session["user_name"]
            # Insert into cart
            sql = "select count(*) from mycart where username=%s and tid=%s"
            val = (username,tid)
            cursor = con.cursor()
            cursor.execute(sql,val)
            count = int(cursor.fetchone()[0])
            # print(count)
            if count ==1:
                return "Ticket already added in cart"
            else:
                sql = "insert into mycart (tid,username,qty) values (%s,%s,%s)"
                val = (tid,username,qty)
                cursor.execute(sql,val)
                con.commit()
                return redirect(url_for("showCart"))
            
def showCart():
    # Check if user is login or not
    if "user_name" in session:
        if request.method == "GET":

            sql = "select * from category"
            cursor = con.cursor()
            cursor.execute(sql)
            cats = cursor.fetchall()

            sql = "select * from mycart_vw where username=%s"
            username = session["user_name"]
            val = (username,)
            cursor = con.cursor()
            cursor.execute(sql,val)
            cart_items = cursor.fetchall()

            sql = "select sum(subtotal) from mycart_vw where username=%s"
            val = (username,)
            cursor.execute(sql,val)
            total = cursor.fetchone()[0]
            session["total"] = total
            return render_template("cart.html",cart_items=cart_items,cats=cats,total=total)
        else:
            action = request.form["action"]
            item_id = request.form["item_id"]
            cursor = con.cursor()
            if action == "delete":
                sql = "delete from mycart where id=%s"
                val = (item_id,)
                cursor.execute(sql,val)
                con.commit()
            else:
                qty = request.form["qty"]
                sql = "update mycart set qty=%s where id=%s"
                val = (qty,item_id)
                cursor.execute(sql,val)
                con.commit()
            return redirect(url_for("showCart"))

    else:
        return redirect(url_for("login"))

def search():
    
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()

  
    query = """
    SELECT t.tid, t.tname, t.price, t.destination, t.image_url,
           t.catid, t.tdate, t.ttime, c.catname, t.source
    FROM ticket t
    JOIN category c ON t.catid = c.catid
    """
    params = []

    if source:
        query += " AND source LIKE %s"
        params.append(f"%{source}%")

    if destination:
        query += " AND destination LIKE %s"
        params.append(f"%{destination}%")
        
    cursor = con.cursor()
    cursor.execute(query, tuple(params))
    tics = cursor.fetchall()  # list of tuples

    # Get categories for navbar or menu
    cursor.execute("SELECT catid, catname FROM category")
    cats = cursor.fetchall()

    category_name = "Search Results"

    return render_template("homepage.html", tics=tics, category_name=category_name, cats=cats)

def makepayment():
    cursor = con.cursor()
    if request.method == "GET":
        sql = "SELECT * FROM category"
        cursor.execute(sql)
        cats = cursor.fetchall()
        return render_template("makepayment.html", cats=cats)
    else:
        card_no = request.form["card_no"]
        
        cvv = request.form["cvv"]
        expiry = request.form["expiry"]

        # Verify card details
        sql = """
            SELECT balance FROM account_details 
            WHERE card_no=%s AND cvv=%s AND expiry=%s
        """
        print("Total from session:", session.get("total"))

        val = (card_no, cvv, expiry)
        cursor.execute(sql, val)
        result = cursor.fetchone()

        if result:
            current_balance = result[0]
            total_amount = session.get("total", 0)

            if current_balance >= total_amount:
                try:
                    # Deduct buyer balance
                    sql_buyer = "UPDATE account_details SET balance = balance - %s WHERE card_no = %s"
                    cursor.execute(sql_buyer, (total_amount, card_no))

                    # Add to owner balance (make sure card_no=222 exists)
                    sql_owner = "UPDATE account_details SET balance = balance + %s WHERE card_no = %s"
                    cursor.execute(sql_owner, (total_amount,  2222222222 ))
                    
                    print("Autocommit:", con.autocommit)
                    con.commit()
                    return redirect(url_for("paymentSuccess"))
                except Exception as e:
                    con.rollback()
                    print("Error during payment transaction:", e)
                   
                    return redirect(url_for("makepayment"))
            else:
                print("Insufficient balance.")
               
                return redirect(url_for("makepayment"))
        else:
            print("Card details not valid.")
            
            return redirect(url_for("makepayment"))



def myBookings():
    if "user_name" not in session:
        return redirect(url_for("login"))
    

    username = session["user_name"]
    cursor = con.cursor(dictionary=True)

    sql = """
        select b.bid, b.booking_date, t.tname, t.source, t.destination, t.tdate, t.ttime, t.price, b.qty, (t.price * b.qty) AS total
        from bookings b
        join ticket t ON b.tid = t.tid
        where b.username = %s
        order by b.booking_date DESC
    """
    cursor.execute(sql, (username,))
    bookings = cursor.fetchall()

    sql = "select * from category"
    cursor = con.cursor()
    cursor.execute(sql)
    cats = cursor.fetchall()
    
    return render_template("myBookings.html", bookings=bookings,cats=cats)


def paymentSuccess():
    if "user_name" not in session:
        return redirect(url_for("login"))
    
    sql = "select * from category"
    cursor = con.cursor()
    cursor.execute(sql)
    cats = cursor.fetchall()

    username = session["user_name"]
    cursor = con.cursor(dictionary=True)

    sql = "select * from mycart where username = %s"
    cursor.execute(sql, (username,))
    cart_items = cursor.fetchall()

    if not cart_items:
        return "Your cart is empty."

    for item in cart_items:
        tid = item["tid"]
        qty = item["qty"]

        cursor.execute("select tdate, ttime FROM ticket where tid = %s", (tid,))
        ticket_info = cursor.fetchone()
        tdate = ticket_info["tdate"]
        ttime = ticket_info["ttime"]

        insert_sql = """
            insert into bookings (username, tid, qty, tdate, ttime)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (username, tid, qty, tdate, ttime))

    cursor.execute("delete from mycart where username = %s", (username,))
    con.commit()

    return render_template("paymentSuccess.html", items=cart_items,cats=cats)



def login():
    if request.method=="GET":
        sql = "select * from category"
        cursor = con.cursor()
        cursor.execute(sql)
        cats = cursor.fetchall()
        return render_template("login.html",cats=cats)
    else:
    
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        sql ="select count(*) from UserLogin where username=%s and password=%s"
        val = (uname,pwd)
        cursor = con.cursor()
        cursor.execute(sql,val)
        count = cursor.fetchone()[0] #  fech first element [0] is used
        if count == 1:
            session["user_name"] = uname
            return redirect(url_for("homepage"))
        else:
            return redirect(url_for("login"))


def signup():
    if request.method=="GET":
        sql = "select * from category"
        cursor = con.cursor()
        cursor.execute(sql)
        cats = cursor.fetchall()
        return render_template("signup.html",cats=cats)
    else:
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        sql ="select count(*) from UserLogin where username=%s"
        val = (uname,)
        cursor = con.cursor()
        cursor.execute(sql,val)
        count = cursor.fetchone()[0] #  fech first element [0] is used
        if count == 1:
            return redirect(url_for("signup"))
        else:
            # Add new user into database
            sql = "insert into UserLogin values(%s,%s)"
            val = (uname,pwd)
            cursor = con.cursor()
            cursor.execute(sql,val)
            con.commit()
            return redirect(url_for("login"))
        

def logout():
    session.clear()
    return redirect(url_for("homepage"))


def about():
    sql = "select * from category"
    cursor = con.cursor()
    cursor.execute(sql)
    cats = cursor.fetchall()

    return render_template("about.html",cats=cats)
