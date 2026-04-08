import mysql.connector
from flask import render_template,request,redirect,url_for

con = mysql.connector.connect(host="localhost",user="root",password="captain07",database="busticketdb")

def addCategory():
    if request.method == "GET":
        return render_template("addCategory.html")
    else:
        try:
            catname = request.form["catname"]
            sql = "insert into Category (catname) values (%s)"
            val =(catname,)
            cursor = con.cursor()
            cursor.execute(sql,val)
            con.commit()
        except:
            pass
        return redirect(url_for("showAllCategories"))


def editCategory(catid):
    if request.method == "GET":
        sql = "select * from Category where catid=%s "
        val = (catid,)
        cursor = con.cursor()
        cursor.execute(sql,val)
        cat = cursor.fetchone()
        return render_template("editCategory.html",cat=cat)
    else:
        catname = request.form["catname"]
       
        sql = "update Category set catname=%s where catid=%s "
        val = (catname,catid)
        cursor = con.cursor()
        cursor.execute(sql,val)
        con.commit()
        return redirect(url_for("showAllCategories"))

def deleteCategory(catid):
    if request.method == "GET":
        return render_template("deleteCategory.html")
    else:
        action = request.form["action"]
        if action == "Yes":
            sql = "delete from Category where catid = (%s) "
            val = (catid,)
            cursor = con.cursor()
            cursor.execute(sql,val)
            con.commit()
        return redirect(url_for("showAllCategories"))

def showAllCategories():
    sql = "select * from category"
    cursor = con.cursor()
    cursor.execute(sql)
    cats = cursor.fetchall()
    return render_template("showAllCategories.html",cats=cats)
