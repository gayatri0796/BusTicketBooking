import mysql.connector
from flask import render_template,request,redirect,url_for
from werkzeug.utils import secure_filename

con = mysql.connector.connect(host="localhost",user="root",password="captain07",database=" busticketdb")

def addTicket():
    if request.method == "GET":
        cursor = con.cursor()
        sql = "select * from category"
        cursor.execute(sql)
        cats = cursor.fetchall()
        return render_template("addTicket.html",cats=cats)
    else:
        try:
            tname = request.form["tname"]
            price = request.form["price"]
            source = request.form["source"]
            destination = request.form["destination"]
            f = request.files["image_url"]
            filename = secure_filename(f.filename)
            filename = "static/Images/"+f.filename
            # This wil save the file to the specified location
            f.save(filename)
            filename = "Images/"+f.filename
            catid = request.form["catid"]
            tdate = request.form["tdate"]
            ttime = request.form["ttime"]

            ttime += ":00"

            # sql = "insert into ticket (tname,price,destination,image_url,catid,tdate,ttime) values (%s,%s,%s,%s,%s,%s,%s)"
            sql = "INSERT INTO ticket (tname, price, source, destination, image_url, catid, tdate, ttime) values (%s, %s, %s, %s, %s, %s, %s, %s)"

            val =(tname,price,source,destination,filename,catid,tdate,ttime)
            cursor = con.cursor()
            cursor.execute(sql,val)
            con.commit()
            print("Ticket inserted successfully!")
        except Exception as e:
            print("Error inserting ticket:", e)
        return redirect(url_for("showAllTickets"))

def showAllTickets():
    # sql = "select * from ticket_cat"
    sql = """
   select t.tid, t.tname, t.price, t.destination, t.image_url,
           t.catid, t.tdate, t.ttime, c.catname, t.source
    from ticket t
    join category c ON t.catid = c.catid
    """
    cursor = con.cursor()
    cursor.execute(sql)
    tics = cursor.fetchall()
    return render_template("showAllTickets.html",tics=tics)

def editTicket(tid):
    if request.method == "GET":
        sql = "select * from ticket where tid=%s "
        val = (tid,)
        cursor = con.cursor()
        cursor.execute(sql,val)
        tic = cursor.fetchone()
        return render_template("editTicket.html",tic=tic)
    else:
        tname = request.form["tname"]
       
        sql = "update ticket set tname=%s where tid =%s"
        val = (tname,tid)
        cursor = con.cursor()
        cursor.execute(sql,val)
        con.commit()
        return redirect(url_for("showAllTickets"))

def deleteTicket(tid):
    if request.method == "GET":
        return render_template("deleteTicket.html")
    else:
        action = request.form["action"]
        if action == "Yes":
            sql = "delete from ticket where tid =%s"
            val = (tid,)
            cursor = con.cursor()
            cursor.execute(sql,val)
            con.commit()
        return redirect(url_for("showAllTickets"))


