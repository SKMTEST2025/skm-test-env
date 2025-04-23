# ------------------------------------------------------------------
#
#	login.py
#
#
#
# ------------------------------------------------------------------

from typing import Any

from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, get_flashed_messages
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import os
import sys
import csv
import pymysql
import pandas as pd
import datetime
import math
from pathlib import Path

# MySQL settings
import mysql.connector
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
#import tkinter as tk
from tkinter import *
#from tkinter import messagebox

import ctypes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import fitz
from PIL import Image, ImageTk

#attention!
# matplotlib.widgets Button is NG!!!
# tkinter's Button is OK!!!
#from matplotlib.widgets import Button
import sqlalchemy

"""
データベースからPDF形式でレポートを生成し、メールに添付して送信する
"""
__author__  = "MindWood"
__version__ = "1.00"
__date__    = "31 Oct 2019"

#import MySQLdb
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle


# constant values
# ------------------------------------------------------------------

flag = False

app = Flask(__name__)
app.secret_key = 'hogehoge'


def conn_db():
    conn = mysql.connector.connect(host='localhost', port='3306', database='mysql', user='root', password='password')

    return conn


#def conn_pysql():
#    conn = pymysql.connect(host='localhost', port=3306, database='mysql', user='root', password='password')

#    return conn


# ------------------------------------------------------------------
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('first.html')


# ------------------------------------------------------------------
@app.route('/login', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    password = request.form['password']

    #form(username, password) to DB check
    #if(logintodb(username,password)):
    logintodb(username, password)
    #print("login is OK")
    #print(session.get('logged_in'))
    # print(session['logged_in'])

    #session['logged_in'] = True

    return home()


def logintodb(username, password):
    sql = "select * from users"

    print("username" + ":" + username)
    print("password" + ":" + password)

    try:
        conn = conn_db()
        #cursor = conn.cursor()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

    except mysql.connector.errors.IntegrityError:
        print("Error occurred")

    print("Select Results")

    flag = False
    for t_rows in rows:
        print(t_rows[0], t_rows[1], t_rows[2])

        if username == t_rows[1]:
            print("username is correct")
            if password == t_rows[2]:
                print("password is correct")
                session['logged_in'] = True
                session['username'] = t_rows[1]
                session['password'] = t_rows[2]
                session['flag'] = True
                break
            else:
                print("password is incorrect!")
                flash("username or password is incorrect!")
        #        if username == t_rows[1]:
        #            print("username is correct")
        #            flag = True
        #        else:
        #            flag = False
        #            print("username is incorrect!")

        #        if password == t_rows[2]:
        #            print("password is correct")
        #            flag = True
        #        else:
        #            flag = False
        #            print("password is incorrect!")

        #        if flag:
        #            session['logged_in'] = True
        #            break
        #session['logged_in'] = False

        #	if request.form['username'] == 'scott' \
        #		and request.form['password'] == 'tiger':
        #		session['logged_in'] = True
        #	else:
        #		flash('wrong username or password!')
        #

def kintaitodb(username, kintai):
    #get session parameters
    username_kintai = session['username']

    #get today format YYYY/MM/DD
    date = format(datetime.date.today(), '%Y/%m/%d')

    #next day
    #date = format(datetime.date(2025,2,15), '%Y/%m/%d')

    #kintai_flg '0': before_clock_in '1' after_clock_in
    kintai_flg = '0'

    print(date)

    #if condition
    #click on clock_in
    if kintai == 'clock_in':
        print("clock_in now!")
    #click on clock_out
    elif kintai == 'clock_out':
        print("clock_out now!")

    conn = conn_db()
    cursor = conn.cursor()

    #if condition
    #click on clock_in
    if kintai == 'clock_in':

        #        select_sql = "INSERT INTO tbl_kintai (syain_id,username,password,kintai_ymd,clock_in_time,clock_out_time,kintai_flg,insert_timestamp,update_timestamp) SELECT syain_id,username,password,kintai_ymd,time(NOW()),clock_out_time,kintai_flg,now(),update_timestamp FROM tbl_kintai where username ='"+username_kintai+"' and kintai_ymd ='"+date+"';"

        # NOT EXISTS where username,kintai_ymd = date_format(now(),'%Y/%m/%d')
        #select_sql = "INSERT INTO tbl_kintai (syain_id,username,password,kintai_ymd,clock_in_time,clock_out_time,kintai_flg,insert_timestamp,update_timestamp) select '00000001','"+username_kintai+"','panda',date_format(now(),'%Y/%m/%d'),time(NOW()),'','"+kintai_flg+"',now(),NULL from dual where not exists (SELECT * FROM tbl_kintai where username ='"+username_kintai+"' and kintai_ymd ='"+date+"');"
        select_sql = "INSERT INTO tbl_kintai (syain_id,username,password,kintai_ymd,clock_in_time,clock_out_time,kintai_flg,insert_timestamp,update_timestamp) select '00000001','" + username_kintai + "','panda','" + date + "',time(NOW()),'','" + kintai_flg + "',now(),NULL from dual where not exists (SELECT * FROM tbl_kintai where username ='" + username_kintai + "' and kintai_ymd ='" + date + "');"

        print("clock_in now!")
        sql = "UPDATE tbl_kintai SET clock_in_time = time(NOW()), kintai_flg='1', insert_timestamp = now() where username ='" + username_kintai + "';"
        print(sql)
    #click on clock_out
    elif kintai == 'clock_out':
        print("clock_out now!")
        select_sql = "UPDATE tbl_kintai SET clock_out_time = time(NOW()), kintai_flg='1', update_timestamp = now() where username ='" + username_kintai + "' and kintai_ymd ='" + date + "' and kintai_flg ='" + kintai_flg + "';"
        print(select_sql)
        #sql = "UPDATE tbl_kintai SET clock_in_time = time(NOW()), kintai_flg='1', update_timestamp = now() where username ='"+username_kintai+"';"
        #print(sql)

    try:
        # cursor.execute(sql)
        cursor.execute(select_sql)
        print("insert Results")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
        #print(cursor.rowcount, "record(s) affected")


@app.route("/kintai", methods=['POST'])
def kintai_insert():
    #form = cgi.FieldStorage()
    #kintai = form.getvalue('kintai')
    print(request.form['kintai'])

    #get form parameters
    #set kintai
    kintai = request.form['kintai']
    print(kintai)

    #if condition
    #click on clock_in
    if kintai == 'clock_in':
        print("clock_in now!")
    #click on clock_out
    elif kintai == 'clock_out':
        print("clock_out now!")

    #clock_in = request.form['clock_in']
    #print(clock_in)
    #print(kintai)
    username_kintai = session['username']
    password_kintai = session['password']
    #logintodb(username,password)
    kintaitodb(username_kintai, kintai)

    return home()


@app.route("/select_kintai")
def get_select_kintai():
    global rows
    print("A")

    sql = "select * from tbl_kintai"

    try:
        conn = conn_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

    except mysql.connector.errors.IntegrityError:
        print("Error occurred")

    print("session flag change to  False")
    session['flag'] = False
    return render_template('first.html', rows=rows)


@app.route("/print_preview")
def get_print_data():

    font_name = "HeiseiKakuGo-W5"  # フォント名
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))  # フォントの登録


    #safe_date = "{:%Y/%m/%d %H:%M}".format(dt + datetime.timedelta(hours=-8))  # 8時間前

    # PDFファイルの初期設定

    # MySQLに接続
    conn = mysql.connector.connect(host='localhost', port='3306', database='mysql', user='root',
                                       password='password')
    cursor = conn.cursor()
    # cursor.execute(sql)
    # rows = cursor.fetchall()

    # 通信機器のマスタ情報取得
    cursor.execute('''
    SELECT username,kintai_ymd, clock_in_time, clock_out_time
    FROM tbl_kintai
    ''')

    rows = cursor.fetchall()
    print(rows)

    def setup_page():
        """フォントを登録し、ヘッダとフッタを設定する"""
        #pdfmetrics.registerFont(UnicodeCIDFont(font_name))  # フォントの登録
        # ヘッダ描画
        c.setFont(font_name, 18)
        c.drawString(10 * mm, height - 15 * mm, "通信機器稼働状況レポート")
        c.setFont(font_name, 9)
        c.drawString(width - 58 * mm, height - 10 * mm, header_date)
        # フッタ描画
        c.drawString(10 * mm, 16 * mm, "直近8時間以内にデータ受信できている端末IDを緑色で表示しています。")
        global page_count
        c.drawString(width - 15 * mm, 5 * mm, "{}頁".format(page_count))  # ページ番号を描画
        page_count += 1

    def control_break():
        """顧客名でコントロールブレイクする"""
        if ctrl_break_key == "": return
        c.showPage()
        setup_page()

    def page_break(n):
        """改ページ処理"""
        n += 1
        if n < 28: return n
        c.showPage()
        setup_page()
        return 0

    header_date = "{:%Y年%-m月%-d日 %-H時%-M分 現在}".format(datetime.datetime.now())
    pdf_filename = "../data/report{:%y%m%d}.pdf".format(datetime.datetime.now())

    c = canvas.Canvas(pdf_filename, pagesize=portrait(A4))  # PDFファイル名と用紙サイズ
    width, height = A4  # 用紙サイズの取得
    c.setAuthor("MindWood")
    c.setTitle("KINTAI_IN/OUT_TIME Monthly report")
    c.setSubject("")

    page_count = customer_no = 1
    ctrl_break_key = ""

    for row_gw in rows:

        if ctrl_break_key != row_gw[0]:
            control_break()
            ctrl_break_key = row_gw[0]
            c.setFont(font_name, 15)
            c.drawString(10 * mm, height - 36 * mm, "{}. {}".format(customer_no, ctrl_break_key))
            customer_no += 1
            data = [["username", "kintai_ymd", "clock_in_time", "clock_out_time"]]  # 通信機器の見出し
            table = Table(data, colWidths=(70 * mm, 40 * mm, 40 * mm, 40 * mm), rowHeights=8 * mm)  # 表の作成
            table.setStyle(TableStyle([
                ("FONT", (0, 0), (-1, -1), font_name, 11),  # フォント
                ("BOX", (0, 0), (-1, -1), 1, colors.black),  # 外側罫線
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),  # 内側罫線
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 文字を縦方向中央に揃える
                ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),  # 灰色で塗り潰す
            ]))
            table.wrapOn(c, 10 * mm, height - 50 * mm)  # 表の位置
            table.drawOn(c, 10 * mm, height - 50 * mm)  # 表の位置
            line_count = 1

        styles = [
            ("FONT", (0, 0), (-1, -1), font_name, 11),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
        # MacAddress = row_gw["MacAddress"]
        # if os.uname()[1] == "ip-172-35-10-XX":  # 特定のサーバなら
        #    MacAddress = "XXXXXXXXXXXX"
        #    styles.append(("BACKGROUND", (3, 0), (3, 0), colors.yellow))  # 黄色で塗り潰す

        # 2025/3/14(FRI) no detail data
        data = [[row_gw[0], row_gw[1], row_gw[2], row_gw[3]]]  # 通信機器の明細データ
        table = Table(data, colWidths=(70 * mm, 40 * mm, 40 * mm, 40 * mm), rowHeights=8 * mm)
        table.setStyle(TableStyle(styles))
        table.wrapOn(c, 10 * mm, height - 50 * mm - 8 * mm * line_count)
        table.drawOn(c, 10 * mm, height - 50 * mm - 8 * mm * line_count)
        line_count = page_break(line_count)

        # データ受信日時の取得
        # cursor.execute('''
        # SELECT hex(TermID) as TermID, from_unixtime(min(Time),"%Y/%m/%d %H:%i:%S") as from_date, from_unixtime(max(Time),"%Y/%m/%d %H:%i:%S") as to_date FROM table0005
        # WHERE MacAddress=0x{} GROUP BY TermID ORDER BY to_date;
        # '''.format(MacAddress))

        # terms = cursor.fetchall()
        # for row_term in terms:
        #    data = [ [ "期間", row_term["from_date"] + " ～ " + row_term["to_date"], "端末ID", row_term["TermID"] ] ]  # 端末の明細データ
        #    table = Table(data, colWidths=(25*mm, 100*mm, 25*mm, 40*mm), rowHeights=8*mm)
        #    styles = [
        #        ("FONT", (0, 0), (-1, -1), font_name, 11),
        #        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        #        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
        #        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        #        ("BACKGROUND", (0, 0), (0, 0), colors.lightgrey),
        #        ("BACKGROUND", (2, 0), (2, 0), colors.lightgrey),
        #    ]
        #    if row_term["to_date"] > safe_date:  # 最終受信日時が直近8時間以内なら
        #        styles.append(("BACKGROUND", (3, 0), (3, 0), colors.palegreen))
        #    table.setStyle(TableStyle(styles))
        #    table.wrapOn(c, 10*mm, height - 50*mm - 8*mm*line_count)
        #    table.drawOn(c, 10*mm, height - 50*mm - 8*mm*line_count)
        #    line_count = page_break(line_count)

    # MySQLの切断
    cursor.close()
    conn.close()

    # PDFファイルに保存
    c.showPage()
    c.save()

    return home()

@app.route("/show_pdf_preview")
def get_pdf_data():

    os.chdir("../data")

    path = r"202503.pdf"

    doc =fitz.open(path)

    zoom = 1.5
    mat = fitz.Matrix(zoom,zoom)

    num_pages = 0
    for i in doc:
        num_pages += 1

        print(i)
        print(num_pages)

    # initialize and set screen size
    root = Tk()
    root.geometry('750x700')

    # add scroll bar
    scrollbar = Scrollbar(root)
    scrollbar.pack(side = RIGHT, fill = Y)

    # add canvas
    canvas = Canvas(root, yscrollcommand = scrollbar.set)
    canvas.pack(side = LEFT, fill = BOTH, expand = 1)


    # define entry point (field for taking inputs)
    entry = Entry(root)

    # add a label for the entry point
    label = Label(root, text="Enter page number to display:")


    def pdf_to_img(page_num):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


    def show_image():
        try:
            page_num = int(entry.get()) - 1
            assert page_num >= 0 and page_num < num_pages
            im = pdf_to_img(page_num)
            img_tk = ImageTk.PhotoImage(im)
            frame = Frame(canvas)
            panel = Label(frame, image=img_tk)
            panel.pack(side="bottom", fill="both", expand="yes")
            frame.image = img_tk
            canvas.create_window(0, 0, anchor='nw', window=frame)
            frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
        except:
            pass


    # add button to display pages
    button = Button(root, text="Show Page", command=show_image)


    # set visual locations
    label.pack(side=TOP, fill=None)
    entry.pack(side=TOP, fill=BOTH)
    button.pack(side=TOP, fill=None)


    entry.insert(0, '1')
    show_image()


    scrollbar.config(command = canvas.yview)
    root.mainloop()


    doc.close()

    return home()

@app.route("/export_csv")
def get_export_csv():
    print("A")

    sql = "select * from tbl_kintai"
    conn = conn_db()
    df = pd.read_sql(sql, conn)

    # os.chdir('data')
    #current_dir = os.path.dirname(os.path.abspath(__file__))
    #parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    #file_path = os.path.join(parent_dir, "exported_csv.csv")

    # directory to csv_export
    path = r"../data/exported_csv.csv"
    df.to_csv(path, encoding="shift_jis")

    #    with open(path, 'w') as f:
    #        for row in rows:
    #            f.write(','.join([str(elem) for elem in row]) + '\n')

    return home()


@app.route("/import_csv")
def get_import_csv():
    print("IMPORT_START")


    # sql = "select * from users"
    conn = conn_db()
    cursor = conn.cursor()

    try:
        #print("B", os.path.dirname(__file__))

        #os.chdir('data')
        #print(os.getcwd())
        #path = r"../data/exported_csv.csv"
        path = r"../data/exported_csv_date.csv"

        my_df = pd.read_csv(path, header=None, encoding='SHIFT_JIS')

        #NULL constraint
        my_df = my_df.where(my_df.notnull(),None)

        #print(my_df)
        #my_df['INSERT_TIMESTAMP'] = pd.to_datetime(my_df[0])
        #my_df['UPDATE_TIMESTAMP'] = pd.to_datetime(my_df[1])

        #print(my_df['INSERT_TIMESTAMP'] )
        #print(my_df['UPDATE_TIMESTAMP'] )

        #insert csv to table
        sql = "INSERT INTO tbl_kintai_date (syain_id,username,password,kintai_ymd,clock_in_time,clock_out_time,kintai_flg,insert_timestamp,update_timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        #print(path)

        # cursor.execute(sql)
        # header exclude
        truncatte_sql = "TRUNCATE table tbl_kintai_date"

        cursor.execute(truncatte_sql)
        data_count = 0
        for line in my_df.values.tolist():
            if not data_count == 0:
            #f.write(','.join([str(elem) for elem in row])+ '\n')
            #cursor.execute("INSERT INTO users (id,username,password) VALUES (%s,%s,%s)",
                           #tuple(line.strip().split(',')))

            #cursor.execute("INSERT INTO tbl_kintai (syain_id,username,password,kintai_ymd,clock_in_time,clock_out_time,kintai_flg,insert_timestamp,update_timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           #tuple(line.strip().split(',')))

                cursor.execute(sql,line)
            #increment
            data_count +=1


        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

    return home()

@app.route("/button_click")
def button_click():
    class Application(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)

            self.master.geometry("300x300")  # ウィンドウサイズ(幅x高さ)

            # ウィンドウの x ボタンが押された時に呼ばれるメソッドを設定
            self.master.protocol("WM_DELETE_WINDOW", self.delete_window)

        def delete_window(self):
            print("ウィンドウのxボタンが押された")

            # 終了確認のメッセージ表示
            ret = messagebox.askyesno(
                title="終了確認",
                message="プログラムを終了しますか？")

            if ret == True:
                # 「はい」がクリックされたとき
                self.master.destroy()



    user = 'root'
    password = 'password'
    host = 'localhost'
    port = 3306
    database = 'mysql'

    url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'

    con = sqlalchemy.create_engine(url)
    #query = 'select insert_timestamp,clock_in_time,clock_out_time from tbl_kintai'
    query = 'select kintai_ymd,clock_in_time,clock_out_time from tbl_kintai'

    df = pd.read_sql_query(query, con)

    #lb = [f"{row}" for row in df['insert_timestamp']]

    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)

    kintai_ymd = []
    for row in df['kintai_ymd']:

        time = row
        strtime = time.strftime("%m/%d")

        print(strtime)
        kintai_ymd.append(strtime)


    clock_in_time = []
    for row in df['clock_in_time']:

        time = row.total_seconds()

        print(time)
        hours = math.floor(time // 3600)

        print(hours)

        clock_in_time.append(hours)


    clock_out_time = []
    for row in df['clock_out_time']:

        time = row.total_seconds()

        print(time)

        hours = math.floor(time // 3600)

        print(hours)

        clock_out_time.append(hours)

    # add to ax.plot(x,y)
    ax.plot(kintai_ymd, clock_in_time, label="clock_in_time")
    ax.plot(kintai_ymd, clock_out_time, label="clock_out_time")

    ax.set_xlabel("DAYS")
    ax.set_ylabel("TIMES")
    ax.set_ylim(0,24)
    ax.legend()
    #plt.plot(result, clock_in_time)

    #date_str = lb.strftime("%m-%d")
    #print(date_str)

    #x= df.plot.bar(title="clock_in_out/month", x='kintai_ymd')
    #y= df.plot.bar(title="clock_in_out/month", y='clock_in_time')
    #df.plot.bar(x='kintai_ymd',y='clock_in_time', figsize=(8,6),, title='clock_in_out/month')
    #plt.xlabel('KINTAI_YMD')
    #plt.ylabel('CLOCK_TIME')



    #df.plot.line(x=x, y="clock_in_time", ax=ax)
    #df.plot.line(x=x, y="clock_out_time", ax=ax)

    #fig = Figure(figsize=(7,5), dpi=100)

    #ax = fig.add_subplot(1,1,1)

    #line = ax.plot(x,y)
    root = tk.Tk()
    root.title("CLOCK_IN_TIME/OUT_TIME / DAYS")
    # set graph to tkinter
    canvas = FigureCanvasTkAgg(fig, root)
    #toolbar = NavigationToolbar2Tk(canvas, root)
    canvas.get_tk_widget().pack()  # show graph 1

    app = Application(master=root)
    app.mainloop()

    return home()

    #root = tk.Tk()
    #root.title('Button')
    #root.geometry('300x300')

    #button = tk.Button(root, text='押す', command=button_click)
    #button.pack()

    #root.mainloop()



    # return render_template('index.html', data=clock_in_time)
    # return render_template('index.html', data=data)
            #first_column_data = input_csv[input_csv.keys()[0]]
            #second_column_data = input_csv[input_csv.keys()[1]]

            #plt.xlabel(input_csv.keys()[0])
            #plt.ylabel(input_csv.keys()[1])

            #plt.plot(first_column_data, second_column_data, linestyle ='solid', marker='o')
            #plt.show()
#                conn = conn_db()
#                df = pd.read_sql(sql, conn)

#                for t_rows in cursor.fetchall():
#                    username.append(t_rows[1])
#                    kintai_ymd.append(t_rows[2])
#                    clock_in_time.append(t_rows[4])
#                    clock_out_time.append(t_rows[5])

#                    username = [s for s in username]
#                    kintai_ymd = [s for s in kintai_ymd]

#                plt.plot(username,kintai_ymd,color = 'red', marker='o')
#                plt.show()

#                print(df)


# ------------------------------------------------------------------
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html')


#
# ------------------------------------------------------------------
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=5000)
# ------------------------------------------------------------------
