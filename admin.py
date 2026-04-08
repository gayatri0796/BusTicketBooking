import mysql.connector
from flask import render_template,request,redirect,url_for,session

con = mysql.connector.connect(host="localhost",user="root",password="captain07",database="busticketdb")

def adminLogin():
    if request.method == "GET":
        return render_template("adminLogin.html")
    else:
        uname = request.form["uname"]
        pwd = request.form["pwd"]
        sql = "select count(*) from adminLogin where username=%s and password=%s"
        val = (uname,pwd)
        cursor = con.cursor()
        cursor.execute(sql,val)
        result = cursor.fetchone()
        if result[0] == 1:
            session["uname"] = uname
            return redirect(url_for("adminDashboard"))
        else:
            return redirect(url_for("adminLogin"))
        
def adminDashboard():
    if "uname" in session:
        return render_template("adminDashboard.html")
    else:
        return redirect(url_for("adminLogin"))
    
def adminLogout():
    if "uname" in session:
        session.clear()
    return redirect(url_for("adminLogin"))