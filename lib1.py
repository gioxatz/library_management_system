# -*- coding: utf-8 -*-
"""
Created on Sat May  6 13:37:17 2023

@author: gioxa
"""
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
import mysql.connector
from datetime import date, timedelta
import datetime

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )

@app.route('/')
def welcome():
    import mysql.connector

    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )
    message = request.args.get('message')
    cursor = db.cursor()
    query ="""Select * from schools"""
    cursor.execute(query)
    schools = cursor.fetchall()

    return render_template('welcome.html', schools=schools, message = message)


@app.route('/admin/schools_list')
def schools_list():
    import mysql.connector

    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )

    cursor = db.cursor()
    query ="""Select * from schools"""
    cursor.execute(query)
    schools = cursor.fetchall()

    return render_template('schools_list.html', schools=schools)

@app.route('/adminlogin')
def adminlogin():
    return render_template('admlogin.html')

@app.route('/admlogin', methods=['POST'])
def admlogin():
    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )
    username = request.form['username']
    password = request.form['password']
    cur = db.cursor()
    cur.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
    admin = cur.fetchone()
    print(admin)
    cur.close()
    if admin is None:
        return render_template('admlogin.html', message='Invalid username or password')
    else:
        return redirect(url_for('admin', adminID=admin[0]))

@app.route('/admin/<int:adminID>')
def admin(adminID):
    cur = db.cursor()
    cur.execute("SELECT * FROM admin WHERE adminID = %s", (adminID,))
    admin = cur.fetchone()
    cur.close()
    cur1 = db.cursor()
    if admin is None:
        return render_template('admlogin.html', message='Please log in first')
    else:
        return render_template('admin.html', admin=admin)



def generate_insert_statements(table_name, cursor, backup_file):
    query = f'SELECT * FROM {table_name}'
    cursor.execute(query)

    data = cursor.fetchall()

    for row in data:
        values = ', '.join([f'"{value}"' if isinstance(value, (str, datetime.date)) else str(value) for value in row])        
        insert_statement = f"INSERT INTO {table_name} VALUES ({values});\n"
        backup_file.write(insert_statement)

def generate_insert_statements_for_student(cursor, backup_file):
        query = f'SELECT userID, num_loans FROM student'
        cursor.execute(query)

        data = cursor.fetchall()

        for row in data:
            values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in row])
            insert_statement = f"INSERT INTO student(userID, num_loans) VALUES ({values});\n"
            backup_file.write(insert_statement)  
            
def generate_insert_statements_for_teacher(cursor, backup_file):
        query = f'SELECT userID, num_loans FROM teacher'
        cursor.execute(query)

        data = cursor.fetchall()

        for row in data:
            values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in row])
            insert_statement = f"INSERT INTO teacher(userID, num_loans) VALUES ({values});\n"
            backup_file.write(insert_statement) 
            
@app.route('/backup')
def backup():
    cursor = db.cursor()
    with open('lib1_backup.sql', 'w', encoding='utf-8') as backup_file:
        tables = ['schools', 'books', 'author', 'is_author', 'subjects', 'keywords', 'has_keywords', 'has_subject',
              'users', 'handler', 'admin', 'school_director', 'review']
        for table_name in tables:
            generate_insert_statements(table_name, cursor, backup_file)
            
        generate_insert_statements_for_student(cursor, backup_file)
        generate_insert_statements_for_teacher(cursor, backup_file)
            
        tables = ['loans', 'has_loan', 'reservations', 'has_reserv']
        for table_name in tables:
            generate_insert_statements(table_name, cursor, backup_file)
            
    cursor.close()
    return redirect(url_for('welcome', message = 'Επιτυχές backup'))


@app.route('/restore')
def restore_database():
    cursor = db.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    tables = ['student', 'teacher', 'has_loan', 'has_reserv', 'reservations', 'loans', 'review', 'school_director', 'admin', 'handler', 'users', 'has_subject', 'has_keywords', 'keywords', 'subjects', 'is_author', 'author', 'books', 'schools']
    for table in tables:
        truncate_query = f"TRUNCATE TABLE {table}"
        cursor.execute(truncate_query)
        db.commit()

    with open('lib1_backup.sql', 'r', encoding='utf-8') as backup_file:
        sql_statements = backup_file.read()

    # Split the SQL statements by semicolon and execute them one by one
    statements = sql_statements.split(';')
    for statement in statements:
        if statement.strip() != '':
            cursor.execute(statement)
            db.commit()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db.commit()
    cursor.close()

    return redirect(url_for('welcome', message='Επιτυχές restoration'))

    
@app.route('/adminlogout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    return redirect('/adminlogin')


@app.route('/helloadmin')
def hello_admin():
    return render_template('hellopage.html')

@app.route('/school/<int:school_id>')
def school(school_id):
    import mysql.connector

    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )

    cursor = db.cursor()
    query = """Select s.*, d.name, d.surname
    from schools s join school_director d on s.schoolID = d.schoolID and s.schoolID = %s
    """
    cursor.execute(query, (school_id,))
    school_data = cursor.fetchone()
    print(school_data)
    cursor.execute("SELECT * FROM books WHERE schoolID = %s", (school_id,))
    books = cursor.fetchall()
    


    return render_template('school.html', school=school_data, books=books)



@app.route('/modify_admin/<int:adminID>', methods=['GET', 'POST'])
def modify_admin(adminID):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor()
        query = "UPDATE admin SET name = %s, surname = %s, email = %s, password = %s WHERE adminID = %s"
        cursor.execute(query, (name, surname, email, password, adminID))
        db.commit()
        cursor.close()

        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        cursor = db.cursor()
        query = "SELECT * FROM admin WHERE adminID = %s"
        cursor.execute(query, (adminID,))
        admin = cursor.fetchone()
        cursor.close()
        return render_template('modify_admin.html', admin=admin)
    
    
@app.route('/modify_school/<int:schoolID>', methods=['GET', 'POST'])
def modify_school(schoolID):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        str_name = request.form['str_name']
        str_number = request.form['str_number']
        zip_code = request.form['zip_code']
        city = request.form['city']
        cursor = db.cursor()
        query = "UPDATE schools SET name = %s, email = %s, phone = %s, str_name = %s, str_number = %s, zip_code = %s, city = %s  WHERE schoolID = %s"
        cursor.execute(query, (name, email, phone, str_name, str_number, zip_code, city, schoolID))
        db.commit()
        cursor.close()

        return redirect(url_for('welcome', message='Επιτυχής αλλαγή'))
    else:
        cursor = db.cursor()
        query = "SELECT * FROM schools WHERE schoolID = %s"
        cursor.execute(query, (schoolID,))
        school = cursor.fetchone()
        cursor.close()
        return render_template('modify_school.html', school = school)
    
    
@app.route('/school/handler/<int:school_id>/<int:handlerID>/books', methods=['GET', 'POST'])
def handlbooks(school_id, handlerID):
    selected_subject_id = 'all'
    search_title = ''
    search_author = ''
    search_copies = ''

    if request.method == 'POST':
        selected_subject_id = request.form['subject_id']
        search_title = request.form['search_title']
        search_author = request.form['search_author']
        search_copies = request.form['search_copies']

        query = """
            SELECT DISTINCT b.ISBN, b.title, b.available_copies, b.schoolID
            FROM books b
            JOIN is_author ia ON b.ISBN = ia.ISBN
            JOIN author a ON ia.authorID = a.authorID
            JOIN has_subject hs ON b.ISBN = hs.ISBN
            JOIN subjects s ON hs.subID = s.subID
            WHERE b.schoolID = %s
        """
        params = [school_id]

        if selected_subject_id != 'all':
            query += "AND hs.subID = %s "
            params.append(selected_subject_id)

        if search_title:
            query += "AND b.title LIKE %s "
            params.append(f"%{search_title}%")

        if search_author:
            query += "AND a.name LIKE %s "
            params.append(f"%{search_author}%")

        if search_copies:
            query += "AND b.available_copies >= %s "
            params.append(int(search_copies))

        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        books = cursor.fetchall()
        cursor.close()

    else:
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT b.ISBN, b.title, b.available_copies, b.schoolID
            FROM books b
            JOIN is_author ia ON b.ISBN = ia.ISBN
            JOIN author a ON ia.authorID = a.authorID
            JOIN has_subject hs ON b.ISBN = hs.ISBN
            JOIN subjects s ON hs.subID = s.subID
            WHERE b.schoolID = %s
        """, (school_id,))
        books = cursor.fetchall()
        cursor.close()

    cu = db.cursor()
    query = """
    SELECT * FROM subjects
    """
    cu.execute(query)
    subjects = cu.fetchall()
    cu.close()

    return render_template('handl_books.html', handlerID=handlerID, school_id = school_id, books=books, subjects=subjects, selected_subject_id=selected_subject_id,
                           search_title=search_title, search_author=search_author, search_copies=search_copies)



def get_all_months():
    months = []
    for month in range(1, 13):
        months.append((month, datetime.date(1900, month, 1).strftime('%B')))
    return months

def get_years():
    current_year = datetime.date.today().year
    years = []
    for year in range(2020, current_year + 1):
        years.append(year)
    return years


@app.route('/loans_by_school', methods=['GET', 'POST'])
def loans_by_school():
    selected_schoolID = 'all'
    c2 = db.cursor()
    q2 = "SELECT schoolID, name FROM schools"
    c2.execute(q2)
    schools = c2.fetchall()
    c2.close()
        
    if request.method == 'POST':
        selected_schoolID = request.form['schoolID']
        selected_year = request.form['year']
        selected_month = request.form['month']
        
        params = []
        q1 = """SELECT distinct l.loanID, u.userID, l.ISBN, l.loan_date, u.name, u.surname, l.pending, l.active, u.schoolID, s.name, b.title
                FROM loans l
                JOIN has_loan hs ON hs.loanID = l.loanID
                JOIN users u ON u.userID = hs.userID
                JOIN schools s ON s.schoolID = u.schoolID
                JOIN books b ON b.ISBN = l.ISBN 
                """
        if selected_schoolID != 'all':
            q1 += "AND s.schoolID = %s "
            params.append(selected_schoolID)
            
        if selected_year:
            q1 += " AND YEAR(l.loan_date) = %s"
            params.append(selected_year)
            
            
        if selected_month:
            q1 += " AND MONTH(l.loan_date) = %s"
            params.append(selected_month)
        
        c1 = db.cursor()
        
        c1.execute(q1, tuple(params))
        loans = c1.fetchall()
        print(loans)
        c1.close()
        
        return render_template('loans_admin.html', loans = loans, schools = schools, months=get_all_months(), years=get_years())
    
    else:
        c11 = db.cursor()
        q11 = """SELECT distinct l.loanID, u.userID, l.ISBN, l.loan_date, u.name, u.surname, l.pending, l.active, u.schoolID, s.name, b.title
                FROM loans l
                JOIN has_loan hs ON hs.loanID = l.loanID
                JOIN users u ON u.userID = hs.userID
                JOIN schools s ON s.schoolID = u.schoolID
                JOIN books b ON b.ISBN = l.ISBN 
                """
        c11.execute(q11, )
        loans = c11.fetchall()
        print(loans)
        c11.close()
        
        
        return render_template('loans_admin.html', schools=schools, loans = loans, months=get_all_months(), years=get_years())


@app.route('/handler/<int:schoolID>/all_loans', methods=['GET', 'POST'])
def loans_of_school(schoolID):
    if request.method == 'POST':
        selected_year = request.form['year']
        selected_month = request.form['month']
        
        params = []
        q1 = """SELECT distinct l.loanID, hs.userID, l.ISBN, l.loan_date, u.name, u.surname, l.pending, l.active, u.schoolID,  b.title
                FROM loans l
                JOIN has_loan hs ON hs.loanID = l.loanID
                JOIN users u ON u.userID = hs.userID
                JOIN books b ON b.ISBN = l.ISBN 
                Where u.schoolID = %s
                """

        params.append(schoolID)
            
        if selected_year:
            q1 += " AND YEAR(l.loan_date) = %s"
            params.append(selected_year)
            
            
        if selected_month:
            q1 += " AND MONTH(l.loan_date) = %s"
            params.append(selected_month)
        
        c1 = db.cursor()
        
        c1.execute(q1, tuple(params))
        loans = c1.fetchall()
        print(loans)
        c1.close()
        
        return render_template('loans_handler.html', loans = loans, schoolID = schoolID, months=get_all_months(), years=get_years())
    
    else:
        c11 = db.cursor()
        q11 = """SELECT distinct l.loanID, hs.userID, l.ISBN, l.loan_date, u.name, u.surname, l.pending, l.active, u.schoolID,  b.title
                FROM loans l
                JOIN has_loan hs ON hs.loanID = l.loanID
                JOIN users u ON u.userID = hs.userID
                JOIN books b ON b.ISBN = l.ISBN 
                WHERE u.schoolID = %s
                """
        c11.execute(q11, (schoolID, ))
        loans = c11.fetchall()
        print(loans)
        c11.close()
        
        
        return render_template('loans_handler.html', schoolID = schoolID, loans = loans, months=get_all_months(), years=get_years())


@app.route('/school/<int:userID>/<int:school_id>/books', methods=['GET', 'POST'])
def books(userID, school_id):
    selected_subject_id = 'all'
    search_title = ''
    search_author = ''
    search_copies = ''

    if request.method == 'POST':
        selected_subject_id = request.form['subject_id']
        search_title = request.form['search_title']
        search_author = request.form['search_author']
        search_copies = request.form['search_copies']

        query = """
            SELECT DISTINCT b.ISBN, b.title, b.available_copies, b.schoolID
            FROM books b
            JOIN is_author ia ON b.ISBN = ia.ISBN
            JOIN author a ON ia.authorID = a.authorID
            JOIN has_subject hs ON b.ISBN = hs.ISBN
            JOIN subjects s ON hs.subID = s.subID
            WHERE b.schoolID = %s
        """
        params = [school_id]

        if selected_subject_id != 'all':
            query += "AND hs.subID = %s "
            params.append(selected_subject_id)

        if search_title:
            query += "AND b.title LIKE %s "
            params.append(f"%{search_title}%")

        if search_author:
            query += "AND a.name LIKE %s "
            params.append(f"%{search_author}%")

        if search_copies:
            query += "AND b.available_copies >= %s "
            params.append(int(search_copies))

        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        books = cursor.fetchall()
        cursor.close()
        print(books)

    else:
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT b.ISBN, b.title, b.available_copies, b.schoolID
            FROM books b
            JOIN is_author ia ON b.ISBN = ia.ISBN
            JOIN author a ON ia.authorID = a.authorID
            JOIN has_subject hs ON b.ISBN = hs.ISBN
            JOIN subjects s ON hs.subID = s.subID
            WHERE b.schoolID = %s
        """, (school_id,))
        books = cursor.fetchall()
        cursor.close()
        print(books)
    
    cu = db.cursor()
    query = """
    SELECT * FROM subjects
    """
    cu.execute(query)
    subjects = cu.fetchall()
    cu.close()
    
    cu1 = db.cursor()
    query1 = """
    SELECT s.num_loans, s.num_reserv FROM student s join users u on s.userID = u.userID where s.userID = %s
    """
    cu1.execute(query1, (userID, ))
    stu_in = cu1.fetchone()
    cu1.close()
    
    cu1 = db.cursor()
    query1 = """
    SELECT s.num_loans, s.num_reserv FROM teacher s join users u on s.userID = u.userID where s.userID = %s
    """
    cu1.execute(query1, (userID, ))
    tea_in = cu1.fetchone()
    cu1.close()
    
    cursor = db.cursor()

    current_date = date.today()
    print(date.today())
    seven_days_ago = current_date - timedelta(days=7)
    print(seven_days_ago)
    query = """
    SELECT loans.loan_date, loans.ISBN
    FROM loans
    JOIN has_loan ON loans.loanID = has_loan.loanID
    WHERE has_loan.userID = %s AND current_date - loans.loan_date > 7 and loans.active = 1
    """
    cursor.execute(query, (userID, ))
    loans = cursor.fetchall()
    cn_ln = len(loans) == 0 
    
    query = """
    SELECT loans.ISBN
    FROM loans
    JOIN has_loan ON loans.loanID = has_loan.loanID
    WHERE has_loan.userID = %s AND loans.active = 1
    """
    cursor.execute(query, (userID, ))
    loaned_ISBN = tuple(row[0] for row in cursor.fetchall())
    cursor.close()
    print(loaned_ISBN)

    if tea_in is None:
        print("stu", stu_in[0], stu_in[1], userID)
        is_student = True
    else:
        print("tea", tea_in[0], tea_in[1], userID)
        is_student = False

    return render_template('books.html', loaned_ISBN = loaned_ISBN, userID=userID, school_id=school_id, cn_ln=cn_ln, is_stu=is_student, nums=stu_in if is_student else tea_in, books=books, subjects=subjects, selected_subject_id=selected_subject_id, search_title=search_title, search_author=search_author, search_copies=search_copies)


@app.route('/school/<int:userID>/handler/<int:school_id>/loan_books', methods=['GET', 'POST'])
def handl_books_loan(userID, school_id):
    selected_subject_id = 'all'
    search_title = ''
    search_author = ''
    search_copies = ''

    if request.method == 'POST':
        selected_subject_id = request.form['subject_id']
        search_title = request.form['search_title']
        search_author = request.form['search_author']
        search_copies = request.form['search_copies']

        query = """
            SELECT DISTINCT b.ISBN, b.title, b.available_copies, b.schoolID
            FROM books b
            JOIN is_author ia ON b.ISBN = ia.ISBN
            JOIN author a ON ia.authorID = a.authorID
            JOIN has_subject hs ON b.ISBN = hs.ISBN
            JOIN subjects s ON hs.subID = s.subID
            WHERE b.schoolID = %s
        """
        params = [school_id]

        if selected_subject_id != 'all':
            query += "AND hs.subID = %s "
            params.append(selected_subject_id)

        if search_title:
            query += "AND b.title LIKE %s "
            params.append(f"%{search_title}%")

        if search_author:
            query += "AND a.name LIKE %s "
            params.append(f"%{search_author}%")

        if search_copies:
            query += "AND b.available_copies >= %s "
            params.append(int(search_copies))

        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        books = cursor.fetchall()
        cursor.close()
        print(books)

    else:
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT b.ISBN, b.title, b.available_copies, b.schoolID
            FROM books b
            JOIN is_author ia ON b.ISBN = ia.ISBN
            JOIN author a ON ia.authorID = a.authorID
            JOIN has_subject hs ON b.ISBN = hs.ISBN
            JOIN subjects s ON hs.subID = s.subID
            WHERE b.schoolID = %s
        """, (school_id,))
        books = cursor.fetchall()
        cursor.close()
        print(books)
    
    cu = db.cursor()
    query = """
    SELECT * FROM subjects
    """
    cu.execute(query)
    subjects = cu.fetchall()
    cu.close()
    
    cu1 = db.cursor()
    query1 = """
    SELECT s.num_loans, s.num_reserv FROM student s join users u on s.userID = u.userID where s.userID = %s
    """
    cu1.execute(query1, (userID, ))
    stu_in = cu1.fetchone()
    cu1.close()
    
    cu1 = db.cursor()
    query1 = """
    SELECT s.num_loans, s.num_reserv FROM teacher s join users u on s.userID = u.userID where s.userID = %s
    """
    cu1.execute(query1, (userID, ))
    tea_in = cu1.fetchone()
    cu1.close()
    
    cursor = db.cursor()

    current_date = date.today()
    print(date.today())
    seven_days_ago = current_date - timedelta(days=7)
    print(seven_days_ago)
    query = """
    SELECT loans.loan_date, loans.ISBN
    FROM loans
    JOIN has_loan ON loans.loanID = has_loan.loanID
    WHERE has_loan.userID = %s AND current_date - loans.loan_date > 7
    """

    cursor.execute(query, (userID, ))
    loans = cursor.fetchall()
    cn_ln = len(loans) == 0  
    
    query = """
    SELECT loans.ISBN
    FROM loans
    JOIN has_loan ON loans.loanID = has_loan.loanID
    WHERE has_loan.userID = %s AND loans.active = 1
    """
    cursor.execute(query, (userID, ))
    loaned_ISBN = tuple(row[0] for row in cursor.fetchall())
    cursor.close()
    print(loaned_ISBN)

    if tea_in is None:
        print("stu", stu_in[0], stu_in[1], userID)
        is_student = True
    else:
        print("tea", tea_in[0], tea_in[1], userID)
        is_student = False

    return render_template('h_l_books.html', loaned_ISBN=loaned_ISBN, userID=userID, school_id=school_id, cn_ln=cn_ln, is_stu=is_student, nums=stu_in if is_student else tea_in, books=books, subjects=subjects, selected_subject_id=selected_subject_id, search_title=search_title, search_author=search_author, search_copies=search_copies)



@app.route('/books/<schoolid>/<isbn>')
def book(isbn, schoolid):
    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )
    
    cursor = db.cursor()
    query = """SELECT b.title, GROUP_CONCAT(a.name SEPARATOR ', '), b.ISBN, b.image, b.publisher, b.available_copies, b.summary, b.num_pages 
            FROM books b
            JOIN is_author ba ON b.ISBN = ba.ISBN and b.ISBN = %s 
            JOIN author a ON ba.authorid = a.authorid 
            WHERE b.schoolID = %s
            """
    
    query2 = """SELECT GROUP_CONCAT(k.keyword SEPARATOR ', ') from books b 
    join has_keywords hs on hs.ISBN = b.ISBN and b.ISBN = %s and b.schoolid =%s
    join keywords k on k.keyword_id = hs.keyword_id """
    cursor.execute(query, (isbn, schoolid))
    book = cursor.fetchone()
    cursor.close()
    cur = db.cursor()
    cur.execute(query2, (isbn, schoolid))
    keyword = cur.fetchall()
    print(book)
    cur.close()
    db.commit()
    cu1 = db.cursor()
    query3 = """SELECT DISTINCT us.name, us.surname, rev.rating, rev.comments from review rev 
	join users us on us.userID = rev.userID where rev.isbn = %s"""
    cu1.execute(query3, (isbn,))
    reviews = cu1.fetchall()
    cu1.close()
    cu2 = db.cursor()
    query4 = """SELECT AVG(rev.rating) from review rev 
	WHERE rev.isbn = %s"""
    cu2.execute(query4, (isbn,))
    average = cu2.fetchone()
    cu2.close()
    
    return render_template('book.html', book = book, keyword = keyword, average = average, reviews = reviews)


@app.route('/books/<int:userID>/<isbn>/write_review',  methods=['GET', 'POST'])
def write_review(userID, isbn):
    if request.method == 'POST':
        rating = request.form['rating']
        comments = request.form['comments']
        print(request.form)
        cursor = db.cursor()
        query = """ INSERT INTO review (ISBN, userID, rating, comments)
        VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (isbn, userID, rating, comments))
        db.commit()
        cursor.close()
        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        return render_template('write_review.html', userID = userID, isbn = isbn)
    

@app.route('/books/<schoolid>/<isbn>/modify', methods=['GET', 'POST'])
def modify_book(isbn, schoolid):
    if request.method == 'POST':
        title = request.form['title']
        publisher = request.form['publisher']
        author = request.form['author']
        num_pages = request.form['num_pages']
        lang = request.form['lang']
        copies = request.form['copies']
        image = request.form['image']
        summary = request.form['summary']
        newsubject = request.form['subjects']
        keywords = request.form['keywords']

        subs, auths, keys = [], [], []
        alsub, alauth, alkey = [], [], []
        print(request.form, schoolid)
        authors = author.split(", ")
        new_sub = newsubject.split(", ")
        key = keywords.split(", ")
        print(authors[0], new_sub[0], key[0])

        cu = db.cursor()
        query = """
        SELECT subject FROM subjects
        """
        cu.execute(query)
        subjects1 = cu.fetchall()
        for sie in subjects1:
            subs.append(sie[0])
        cu.close()
        
        cu1 = db.cursor()
        query1 = """
        SELECT keyword FROM keywords
        """
        cu1.execute(query1)
        keywords1 = cu1.fetchall()
        for keye in keywords1:
            keys.append(keye[0])
        cu1.close()
        
        cu = db.cursor()
        query = """
        SELECT DISTINCT name FROM author join is_author on author.authorID = is_author.authorID
        """
        cu.execute(query)
        auth = cu.fetchall()
        for aur in auth:
            auths.append(aur[0])
        cu.close()
        for ns in new_sub:
            if(ns not in subs):
                alsub.append(ns) #νεες κατηγορίες
        for au in authors:
            if(au not in auths):
                alauth.append(au)
        for ke in key:
            if(ke not in keys):
                alkey.append(ke)
                
        print(alauth)
        print(alsub)
        print(alkey)
            
        cursor = db.cursor()
        query = """ UPDATE books SET title = %s, publisher = %s, num_pages = %s, lang = %s, copies=%s, image = %s, summary = %s
           where isbn = %s and schoolID = %s"""
        cursor.execute(query, (title, publisher, num_pages, lang, copies, image, summary, isbn, schoolid))
        cursor.close()
        db.commit()
        
        if alauth:
            cursor = db.cursor()
            for au in alauth:
                query = "INSERT INTO author (name) VALUES (%s)"
                cursor.execute(query, (au,))
            cursor.close()
            db.commit()
        
        if alsub:
            cursor = db.cursor()
            for ns in alsub:
                query = "INSERT INTO subjects (subject) VALUES (%s)"
                cursor.execute(query, (ns,))
            cursor.close()
            db.commit()
        
        if alkey:
            cursor = db.cursor()
            for ky in alkey:
                query = "INSERT INTO keywords (keyword) VALUES (%s)"
                cursor.execute(query, (ky,))
            cursor.close()
            db.commit()
        
        cursor = db.cursor()
        for au in alauth:
            query = "SELECT authorID FROM author WHERE name = %s"
            cursor.execute(query, (au,))
            authorID = cursor.fetchone()[0]
            query = "INSERT INTO is_author (ISBN, authorID) VALUES (%s, %s)"
            cursor.execute(query, (isbn, authorID))
            db.commit()
        cursor.close()
        
        cursor = db.cursor()
        for ns in alsub:
            query = "SELECT subID FROM subjects WHERE subject = %s"
            cursor.execute(query, (ns,))
            subID = cursor.fetchone()[0]
            query = "INSERT INTO has_subject (ISBN, subID) VALUES (%s, %s)"
            cursor.execute(query, (isbn, subID))
            db.commit()
        cursor.close()

        
        cursor = db.cursor()
        for k in alkey:
            query = "SELECT keyword_id FROM keywords WHERE keyword = %s"
            cursor.execute(query, (k,))
            keyword_id = cursor.fetchone()[0]
            query = "INSERT INTO has_keywords (ISBN, keyword_id) VALUES (%s, %s)"
            cursor.execute(query, (isbn, keyword_id))
            db.commit()
        cursor.close()

        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        cursor = db.cursor()
        query = """
        SELECT b.isbn, b.schoolID, b.title, b.publisher, b.copies, b.image, b.summary, b.available_copies, b.lang, b.num_pages, GROUP_CONCAT(a.name SEPARATOR ', ')
        FROM books b
        JOIN is_author ba ON b.ISBN = ba.ISBN and b.ISBN = %s
        JOIN author a ON ba.authorid = a.authorid
        WHERE b.schoolID = %s
        """
        cursor.execute(query, (isbn, schoolid))
        book = cursor.fetchone()
        cursor.close()

        c1 = db.cursor()
        q1 = """
        SELECT GROUP_CONCAT(k.keyword SEPARATOR ', ')
        from keywords k join has_keywords hs on k.keyword_ID = hs.keyword_ID
        join books b on b.ISBN = hs.ISBN and b.schoolID = %s and b.ISBN = %s
        """
        c1.execute(q1, (schoolid, isbn))
        keys = c1.fetchone()[0]
        c1.close()

        c1 = db.cursor()
        q1 = """
        SELECT GROUP_CONCAT(s.subject SEPARATOR ', ')
        from subjects s join has_subject hs on s.subID = hs.subID
        join books b on b.ISBN = hs.ISBN and b.schoolID = %s and b.ISBN = %s
        """
        c1.execute(q1, (schoolid, isbn))
        subs = c1.fetchone()[0]
        c1.close()

        return render_template('modbook.html', book=book, isbn=isbn, schoolid=schoolid, keys=keys, subs=subs)



@app.route('/school/<int:schoolID>/newbook', methods=['GET', 'POST'])
def newbook(schoolID):
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publisher = request.form['publisher']
        author = request.form['author']
        num_pages = request.form['num_pages']
        lang = request.form['lang']
        copies = request.form['copies']
        image = request.form['image']
        summary = request.form['summary']
        newsubject = request.form['subjects']
        keywords = request.form['keywords']
        
        subs, auths, keys = [], [], []
        alsub, alauth, alkey = [], [], []
        print(request.form, schoolID)
        authors = author.split(", ")
        new_sub = newsubject.split(", ")
        key = keywords.split(", ")
        print(authors[0], new_sub[0], key[0])
        
        cu = db.cursor()
        query = """
        SELECT subject FROM subjects
        """
        cu.execute(query)
        subjects1 = cu.fetchall()
        for sie in subjects1:
            subs.append(sie[0])
        cu.close()
        
        cu1 = db.cursor()
        query1 = """
        SELECT keyword FROM keywords
        """
        cu1.execute(query1)
        keywords1 = cu1.fetchall()
        for keye in keywords1:
            keys.append(keye[0])
        cu1.close()
        
        cu = db.cursor()
        query = """
        SELECT DISTINCT name FROM author join is_author on author.authorID = is_author.authorID
        """
        cu.execute(query)
        auth = cu.fetchall()
        for aur in auth:
            auths.append(aur[0])
        cu.close()
        for ns in new_sub:
            if(ns not in subs):
                alsub.append(ns) #νεες κατηγορίες
        for au in authors:
            if(au not in auths):
                alauth.append(au)
        for ke in key:
            if(ke not in keys):
                alkey.append(ke)
                
        print(alauth)
        print(alsub)
        print(alkey)
            
        cursor = db.cursor()
        query = """ INSERT INTO books (ISBN, schoolID, title, publisher, num_pages, lang, copies, image, summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (isbn, schoolID, title, publisher, num_pages, lang, copies, image, summary))
        cursor.close()
        db.commit()
        
        if alauth:
            cursor = db.cursor()
            for au in alauth:
                query = "INSERT INTO author (name) VALUES (%s)"
                cursor.execute(query, (au,))
            cursor.close()
            db.commit()
        
        if alsub:
            cursor = db.cursor()
            for ns in alsub:
                query = "INSERT INTO subjects (subject) VALUES (%s)"
                cursor.execute(query, (ns,))
            cursor.close()
            db.commit()
        
        if alkey:
            cursor = db.cursor()
            for ky in alkey:
                query = "INSERT INTO keywords (keyword) VALUES (%s)"
                cursor.execute(query, (ky,))
            cursor.close()
            db.commit()
        
        cursor = db.cursor()
        for au in authors:
            query = "SELECT authorID FROM author WHERE name = %s"
            cursor.execute(query, (au,))
            authorID = cursor.fetchone()[0]
            query = "INSERT INTO is_author (ISBN, authorID) VALUES (%s, %s)"
            cursor.execute(query, (isbn, authorID))
            db.commit()
        cursor.close()
        
        cursor = db.cursor()
        for ns in new_sub:
            query = "SELECT subID FROM subjects WHERE subject = %s"
            cursor.execute(query, (ns,))
            subID = cursor.fetchone()[0]
            query = "INSERT INTO has_subject (ISBN, subID) VALUES (%s, %s)"
            cursor.execute(query, (isbn, subID))
            db.commit()
        cursor.close()

        
        cursor = db.cursor()
        for k in key:
            query = "SELECT keyword_id FROM keywords WHERE keyword = %s"
            cursor.execute(query, (k,))
            keyword_id = cursor.fetchone()[0]
            query = "INSERT INTO has_keywords (ISBN, keyword_id) VALUES (%s, %s)"
            cursor.execute(query, (isbn, keyword_id))
            db.commit()
        cursor.close()
        
        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        return render_template('newbook.html', schoolID = schoolID)
    

@app.route('/school/<int:schoolID>/teacherlogin')
def teacherlogin(schoolID):
    return render_template('teacher_login.html', schoolID = schoolID)


@app.route('/school/<int:schoolID>/teachlogin', methods=['POST'])
def teachlogin(schoolID):
    db = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="lib1"
    )
    username = request.form['username']
    password = request.form['password']
    cur = db.cursor()
    cur.execute("""SELECT users.* FROM teacher
    join users on users.userID = teacher.userID WHERE username = %s AND password = %s AND active = 1""", (username, password))
    teacher = cur.fetchone()
    print(teacher)
    cur.close()
    if teacher is None:
        return render_template('teacher_login.html', schoolID = schoolID, message='Invalid username or password')
    else:
        return redirect(url_for('user1', schoolID = schoolID, userID=teacher[0]))
    

@app.route('/school/<int:schoolID>/teacher/<int:userID>', methods=['GET', 'POST'])
def user1(schoolID, userID):
    cur = db.cursor()
    cur.execute("""SELECT users.*, teacher.* FROM teacher
    JOIN users ON users.userID = teacher.userID WHERE users.userID = %s""", (userID,))
    user = cur.fetchone()
    cur.close()

    cu = db.cursor()
    query = """
    SELECT * FROM subjects
    """
    cu.execute(query)
    subjects = cu.fetchall()
    cu.close()

    if user is None:
        return render_template('teacher_login.html', schoolID=schoolID, message='Please log in first')
    else:
        if request.method == 'POST':
            selected_subject_id = request.form['subject_id']
            return redirect(url_for('books', school_id=schoolID, userID=userID, subject_id=selected_subject_id))
        else:
            return render_template('teacher.html', user=user, subjects=subjects)


@app.route('/school/teacher/modify_teacher/<int:userid>', methods=['GET', 'POST'])
def modify_teacher(userid):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        query = "UPDATE users SET name = %s, surname = %s, email = %s, password = %s WHERE userID = %s"
        cursor.execute(query, (name, surname, email, password, userid))
        db.commit()
        cursor.close()

        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        cursor = db.cursor()
        query = "SELECT * FROM users WHERE userID = %s"
        cursor.execute(query, (userid,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('modify_teacher.html', user=user)
    

@app.route('/school/student/modify_student/<int:handlerID>/<int:userid>', methods=['GET', 'POST'])
def modify_student(handlerID, userid):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        query = "UPDATE users SET name = %s, surname = %s, email = %s, password = %s WHERE userid = %s"
        cursor.execute(query, (name, surname, email, password, userid))
        db.commit()
        cursor.close()

        return redirect(url_for('handler', handlerID=handlerID))
    else:
        cursor = db.cursor()
        query = "SELECT * FROM users WHERE userID = %s"
        cursor.execute(query, (userid,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('modify_student.html', user=user, handlerID = handlerID)


@app.route('/school/<int:schoolID>/student_registration', methods=['GET', 'POST'])
def student_registration(schoolID):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        birthdate = request.form['birthdate']
        print(request.form, schoolID)
        cu1 = db.cursor()
        cu1.execute("SELECT email FROM users where email = %s", (email, ))
        tr1 = cu1.fetchone()
        cu1.close()
        cu2 = db.cursor()
        cu2.execute("SELECT username FROM users where username = %s", (username, ))
        tr2 = cu2.fetchone()
        cu2.close()
        if tr1 is not None or tr2 is not None:
            return render_template('user_register.html', schoolID = schoolID, message='Το email ή το username που καταχωρήσατε υπάρχει ήδη')
                    
        cursor = db.cursor()
        query = """ INSERT INTO users (schoolID, name, surname, email, username, password, birthdate)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (schoolID, name, surname, email, username, password, birthdate))
        db.commit()
        cursor.close()
        cursor1 = db.cursor()
        query1 = """ SELECT userID FROM users ORDER BY userID DESC LIMIT 1"""
        cursor1.execute(query1)
        userID = cursor1.fetchone()[0]
        db.commit()
        cursor1.close()
        cursor2 = db.cursor()
        query2 = """ INSERT INTO student (userID) VALUES (%s)"""
        cursor2.execute(query2, (userID, ))
        db.commit()
        cursor2.close()
        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        return render_template('user_register.html', schoolID = schoolID)
    
    
@app.route('/school/<int:schoolID>/teacher_registration', methods=['GET', 'POST'])
def teacher_registration(schoolID):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        birthdate = request.form['birthdate']
        print(request.form, schoolID)
        cu1 = db.cursor()
        cu1.execute("SELECT email FROM users where email = %s", (email, ))
        tr1 = cu1.fetchone()
        cu1.close()
        cu2 = db.cursor()
        cu2.execute("SELECT username FROM users where username = %s", (username, ))
        tr2 = cu2.fetchone()
        cu2.close()
        if tr1 is not None or tr2 is not None:
            return render_template('teacher_register.html', schoolID = schoolID, message='Το email ή το username που καταχωρήσατε υπάρχει ήδη')
        
        cursor = db.cursor()
        query = """ INSERT INTO users (schoolID, name, surname, email, username, password, birthdate)
        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (schoolID, name, surname, email, username, password, birthdate))
        db.commit()
        cursor.close()
        
        cursor1 = db.cursor()
        query1 = """ SELECT userID FROM users ORDER BY userID DESC LIMIT 1"""
        cursor1.execute(query1)
        userID = cursor1.fetchone()[0]
        db.commit()
        cursor1.close()
        
        cursor2 = db.cursor()
        query2 = """ INSERT INTO teacher (userID) VALUES (%s)"""
        cursor2.execute(query2, (userID, ))
        db.commit()
        cursor2.close()
        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        return render_template('teacher_register.html', schoolID = schoolID)
    


@app.route('/school/<int:schoolID>/handler_registration', methods=['GET', 'POST'])
def handler_registration(schoolID):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        print(request.form, schoolID)
        cu1 = db.cursor()
        cu1.execute("SELECT email FROM handler where email = %s", (email, ))
        tr1 = cu1.fetchone()
        cu1.close()
        cu2 = db.cursor()
        cu2.execute("SELECT username FROM handler where username = %s", (username, ))
        tr2 = cu2.fetchone()
        cu2.close()
        if tr1 is not None or tr2 is not None:
            return render_template('handler_register.html', schoolID = schoolID, message='Το email ή το username που καταχωρήσατε υπάρχει ήδη')
                    
                    
        cursor = db.cursor()
        query = """ INSERT INTO handler (schoolID, firstname, lastname, email, username, password)
        VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (schoolID, name, surname, email, username, password))
        db.commit()
        cursor.close()
        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        return render_template('handler_register.html', schoolID = schoolID)


@app.route('/school/<int:schoolID>/student/<int:userID>/reservations')
def showreserv_stud(schoolID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.res_date, r.resID
        FROM reservations AS r
        JOIN has_reserv AS hs ON r.resID = hs.resID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        """
    cur.execute(query, (userID, ))
    stu_res = cur.fetchall()
    print(stu_res)
    return render_template('stud_reservations.html', schoolID = schoolID, userID = userID, stu_res = stu_res)
           

@app.route('/school/<int:schoolID>/teacher/<int:userID>/reservations')
def showreserv_teach(schoolID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.res_date, r.resID
        FROM reservations AS r
        JOIN has_reserv AS hs ON r.resID = hs.resID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        """
    cur.execute(query, (userID, ))
    tea_res = cur.fetchall()
    print(tea_res)
    return render_template('tea_reservations.html', schoolID = schoolID, userID = userID, tea_res = tea_res)
           

@app.route('/school/<int:schoolID>/student/<int:userID>/newreservation/<int:ISBN>')
def stud_res(schoolID, userID, ISBN):
    cur1 = db.cursor()
    query1 = """
        INSERT INTO reservations values (default, %s, default, default)
        """
    cur1.execute(query1, (ISBN,))
    db.commit()
    q2 = "SELECT resID from reservations ORDER BY resID DESC LIMIT 1"
    cur1.execute(q2)
    resID = cur1.fetchone()[0]
    cur1.close()
    
    
    cur2 = db.cursor()
    query2 = """
    INSERT INTO has_reserv (resID, userID) VALUES (%s, %s)
        """
    cur2.execute(query2, (resID, userID))
    db.commit()
    cur2.close()
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))


@app.route('/school/<int:schoolID>/teacher/<int:userID>/newreservation/<int:ISBN>')
def teach_res(schoolID, userID, ISBN):
    cur1 = db.cursor()
    query1 = """
        INSERT INTO reservations values (default, %s, default, default)
        """
    cur1.execute(query1, (ISBN,))
    db.commit()
    # resID = cur1.lastrowid
    q2 = "SELECT resID from reservations ORDER BY resID DESC LIMIT 1"
    cur1.execute(q2)
    resID = cur1.fetchone()[0]
    cur1.close()
    
    cur2 = db.cursor()
    query2 = """
    INSERT INTO has_reserv (resID, userID) VALUES (%s, %s)
        """
    cur2.execute(query2, (resID, userID))
    db.commit()
    cur2.close()
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))

@app.route('/school/<int:schoolID>/<int:userID>/delete_res/<int:resID>')
def delete_res(schoolID, userID, resID):
    cur1 = db.cursor()
    cur1.execute("SELECT userID FROM teacher WHERE userID = %s", (userID,))
    teacher = cur1.fetchone()
    db.commit()
    cur1.close()
    print(teacher)
    
    cur2 = db.cursor()
    cur2.execute("DELETE FROM has_reserv WHERE resID = %s", (resID,))
    db.commit()
    cur2.close()
    
    cur4 = db.cursor()
    cur4.execute("DELETE FROM reservations WHERE resID = %s", (resID,))
    db.commit()
    cur4.close()
    
    
    if teacher:
        cur3 = db.cursor()
        cur3.execute("UPDATE teacher SET num_reserv = num_reserv - 1 WHERE userID = %s", (userID,))
        db.commit()
        cur3.close()
        return redirect(url_for('user1', schoolID = schoolID, userID = userID))
    else:
        cur3 = db.cursor()
        cur3.execute("UPDATE student SET num_reserv = num_reserv - 1 WHERE userID = %s", (userID,))
        db.commit()
        cur3.close()
        return redirect(url_for('student', schoolID = schoolID, userID = userID))

    


@app.route('/school/<int:schoolID>/student/<int:userID>/loans')
def showloans_stud(schoolID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.loan_date, r.loanID, r.active, r.pending
        FROM loans AS r
        JOIN has_loan AS hs ON r.loanID = hs.loanID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        """
    cur.execute(query, (userID, ))
    stu_ln = cur.fetchall()
    print(stu_ln)
    return render_template('stud_loans.html', schoolID = schoolID, userID = userID, stu_ln = stu_ln)
           

@app.route('/school/<int:schoolID>/teacher/<int:userID>/loans')
def showloans_teach(schoolID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.loan_date, r.loanID, r.active, r.pending
        FROM loans AS r
        JOIN has_loan AS hs ON r.loanID = hs.loanID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        """
    cur.execute(query, (userID, ))
    tea_ln = cur.fetchall()
    print(tea_ln)
    return render_template('tea_loans.html', schoolID = schoolID, userID = userID, tea_ln = tea_ln)
           

@app.route('/loan_plus_7/<int:loanID>')
def loan_plus_7(loanID):
    c1 = db.cursor()
    q1 = """
    UPDATE loans l SET l.loan_date = DATE_ADD(loan_date, INTERVAL 7 DAY), l.end_date=DATE_ADD(end_date, INTERVAL 7 DAY)
    WHERE l.loanID = %s
    """
    c1.execute(q1, (loanID, ))
    db.commit()
    c1.close()
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))

@app.route('/success')
def success():
    return render_template('success.html')



@app.route('/school/<int:schoolID>/student/<int:userID>/newloan/<int:ISBN>')
def s_newloan(schoolID, userID, ISBN):
    cur1 = db.cursor()
    q1 = """
        INSERT INTO loans (ISBN, active) VALUES (%s, 1)
        """
    cur1.execute(q1, (ISBN, ))
    db.commit()
    # loanID = cur1.lastrowid
    q2 = "SELECT loanID from loans ORDER BY loanID DESC LIMIT 1"
    cur1.execute(q2)
    loanID = cur1.fetchone()[0]
    cur1.close()
    
    cur2 = db.cursor()
    q2 = """
    INSERT INTO has_loan VALUES (%s, %s)
    """
    cur2.execute(q2, (loanID, userID))
    db.commit()
    cur2.close()
    
    cur3 = db.cursor()
    q3 = """
    UPDATE student SET num_loans = num_loans + 1 where userID = %s 
    """
    cur3.execute(q3, (userID,))
    db.commit()
    cur3.close()
    
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))


@app.route('/school/<int:schoolID>/teacher/<int:userID>/newloan/<int:ISBN>')
def t_newloan(schoolID, userID, ISBN):
    cur1 = db.cursor()
    q1 = """
        INSERT INTO loans (ISBN, active) VALUES (%s, 1)
        """
    cur1.execute(q1, (ISBN, ))
    db.commit()
    # loanID = cur1.lastrowid
    q2 = "SELECT loanID from loans ORDER BY loanID DESC LIMIT 1"
    cur1.execute(q2)
    loanID = cur1.fetchone()[0]
    cur1.close()
    
    cur2 = db.cursor()
    q2 = """
    INSERT INTO has_loan VALUES (%s, %s)
    """
    cur2.execute(q2, (loanID, userID))
    db.commit()
    cur2.close()
    
    cur3 = db.cursor()
    q3 = """
    UPDATE teacher SET num_loans = num_loans + 1 where userID = %s 
    """
    cur3.execute(q3, (userID,))
    db.commit()
    cur3.close()
    
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    


@app.route('/under_construction')
def construction():
    return render_template("/construction.html")


@app.route('/school/<int:schoolID>/studentlogin')
def studentlogin(schoolID):
    return render_template('/student_login.html', schoolID = schoolID) 


@app.route('/school/<int:schoolID>/studlogin', methods=['POST'])
def studlogin(schoolID):
    username = request.form['username']
    password = request.form['password']
    cur = db.cursor()
    cur.execute("""SELECT users.* FROM student
    join users on users.userID = student.userID WHERE username = %s AND password = %s and active = 1""", (username, password))
    student = cur.fetchone()
    print(student)
    cur.close()
    if student is None:
        return render_template('student_login.html', schoolID = schoolID, message='Invalid username or password')
    else:
        return redirect(url_for('student', schoolID = schoolID, userID=student[0]))
    

@app.route('/school/<int:schoolID>/student/<int:userID>', methods=['GET', 'POST'])
def student(schoolID, userID):
    cur = db.cursor()
    cur.execute("""SELECT users.*, student.* FROM student
    join users on users.userID = student.userID WHERE users.userID = %s""", (userID,))
    user = cur.fetchone()
    cur.close()
    
    if user is None:
        return render_template('student_login.html', schoolID = schoolID, message='Please log in first')
    else:
        return render_template('student.html', user=user)


@app.route('/handlers_list', methods=['GET', 'POST'])
def handlers_list():
    c1 = db.cursor()
    q1 = "SELECT handler.*, schools.name from handler join schools on schools.schoolID = handler.schoolID"
    c1.execute(q1)
    handlers = c1.fetchall()
    return render_template("handlers_list.html", handlers = handlers)


@app.route('/school/<int:handlerID>/activate', methods=['POST'])
def activate_handler(handlerID):
    cursor = db.cursor()
    cursor.execute("UPDATE handler SET active = 1 WHERE handlerID = %s", (handlerID,))
    db.commit()
    cursor.close()
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))


@app.route('/school/<int:handlerID>/deactivate', methods=['POST'])
def deactivate_handler(handlerID):
    cursor = db.cursor()
    cursor.execute("UPDATE handler SET active = 0 WHERE handlerID = %s", (handlerID,))
    db.commit()
    cursor.close()
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))

@app.route('/school/<int:handlerID>/delete', methods=['POST'])
def delete_handler(handlerID):
    cursor = db.cursor()
    cursor.execute("DELETE FROM handler WHERE handlerID = %s", (handlerID, ))
    db.commit()
    cursor.close()
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))

@app.route('/school/<int:schoolID>/handlerlogin')
def handlerlogin(schoolID):
    return render_template('handler_login.html', schoolID = schoolID)


@app.route('/school/handllogin', methods=['POST'])
def handllogin():
    username = request.form['username']
    password = request.form['password']
    cur = db.cursor()
    cur.execute("""SELECT handler.* FROM handler
    WHERE username = %s AND password = %s AND active = 1""", (username, password))
    handler = cur.fetchone()
    print(handler)
    cur.close()
    if handler is None:
        return render_template('handler_login.html', message='Invalid username or password')
    else:
        return redirect(url_for('handler', handlerID=handler[0]))
    

@app.route('/school/<int:user_id>/card')
def user_card(user_id):
    c = db.cursor()
    q = """
    SELECT u.name, u.surname, u.email, u.birthdate, s.name, current_date
    FROM users u join schools s on s.schoolID = u.schoolID
    WHERE u.userID = %s
    """
    c.execute(q, (user_id, ))
    user = c.fetchone()
    print(user)
    return render_template('user_card.html', user = user)
    
    
@app.route('/school/handler/<int:handlerID>/activate/<int:user_id>', methods=['POST', 'GET'])
def activate_user(handlerID, user_id):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET active = 1 WHERE userID = %s", (user_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('user_card', user_id=user_id))


@app.route('/school/handler/<int:handlerID>/deactivate/<int:user_id>', methods=['POST', 'GET'])
def deactivate_user(handlerID, user_id):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET active = 0 WHERE userID = %s", (user_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('handler', handlerID=handlerID))


@app.route('/school/handler/<int:handlerID>/delete/<int:user_id>', methods=['POST', 'GET'])
def delete_user(handlerID, user_id):
    cur1 = db.cursor()
    cur1.execute("SELECT userID FROM teacher WHERE userID = %s", (user_id,))
    teacher = cur1.fetchone()
    db.commit()
    cur1.close()
    print(teacher)
    
    cur2 = db.cursor()
    cur2.execute("SELECT resID FROM has_reserv WHERE userID = %s", (user_id,))
    resIDs = cur2.fetchall()
    db.commit()
    cur2.close()
    
    cur2 = db.cursor()
    cur2.execute("SELECT loanID FROM has_loan WHERE userID = %s", (user_id,))
    loanIDs = cur2.fetchall()
    db.commit()
    cur2.close()
    
    cur2 = db.cursor()
    cur2.execute("SELECT l.ISBN FROM loans l join has_loan hs on hs.loanID = l.loanID where hs.userID = %s", (user_id,))
    books = cur2.fetchall()
    db.commit()
    cur2.close()
    
    cur3 = db.cursor()
    for resID in resIDs: 
        cur3.execute("DELETE FROM has_reserv WHERE resID = %s", resID)
    db.commit()
    cur3.close()
    
    cur3 = db.cursor()
    for loanID in loanIDs: 
        cur3.execute("DELETE FROM has_loan WHERE loanID = %s", loanID)
    db.commit()
    cur3.close()
    
    
    cur4 = db.cursor()
    for resID in resIDs:
        cur4.execute("DELETE FROM reservations WHERE resID = %s", resID)
    db.commit()
    cur4.close()
    
    cur4 = db.cursor()
    for loanID in loanIDs:
        cur4.execute("DELETE FROM loans WHERE loanID = %s", loanID)
    db.commit()
    cur4.close()
    
    cur5 = db.cursor()
    cur5.execute("DELETE FROM review WHERE userID = %s", (user_id,))
    db.commit()
    cur5.close()
    
    for book in books:
        cur5 = db.cursor()
        cur5.execute("UPDATE books SET available_copies = available_copies + 1 WHERE ISBN = %s", (book,))
        db.commit()
        cur5.close()

    if teacher:
        cur2 = db.cursor()
        cur2.execute("DELETE FROM teacher WHERE userID = %s", (user_id,))
        db.commit()
        cur2.close()
    else:
        cur2 = db.cursor()
        cur2.execute("DELETE FROM student WHERE userID = %s", (user_id,))
        db.commit()
        cur2.close()

    cur3 = db.cursor()
    cur3.execute("DELETE FROM users WHERE userID = %s", (user_id,))
    db.commit()
    cur3.close()
    return redirect(url_for('handler', handlerID=handlerID))


@app.route('/school/handler/<int:handlerID>', methods=['GET', 'POST'])
def handler(handlerID):
    cur = db.cursor()
    cur.execute("""SELECT handler.* FROM handler
    WHERE handler.handlerID = %s""", (handlerID,))
    handler = cur.fetchone()
    cur.close()
    cu = db.cursor()
    query = """
    SELECT * FROM subjects
    """
    cu.execute(query)
    subjects = cu.fetchall() 
    cu.close()
    cu1 = db.cursor()
    q1 = """SELECT u.*, t.* FROM users u join teacher t on u.userID = t.userID where u.schoolID = %s"""
    cu1.execute(q1, (handler[1], ))
    tea_users = cu1.fetchall()
    cu1.close()
    cu2 = db.cursor()
    q2 = """SELECT u.*, t.* FROM users u join student t on u.userID = t.userID where u.schoolID = %s"""
    cu2.execute(q2, (handler[1], ))
    stu_users = cu2.fetchall()
    cu2.close()
    if handler is None:
        return render_template('handler_login.html', message='Please log in first')
    else:
        if request.method == 'POST':
                selected_subject_id = request.form['subject_id']
                return redirect(url_for('books', school_id=user[1], subject_id=selected_subject_id))
        
        cu1 = db.cursor()
        q1 = """SELECT u.*, t.* FROM users u join teacher t on u.userID = t.userID where u.schoolID = %s"""
        cu1.execute(q1, (handler[1],))
        tea_users = cu1.fetchall()
        cu1.close()
        
        cu2 = db.cursor()
        q2 = """SELECT u.*, t.* FROM users u join student t on u.userID = t.userID where u.schoolID = %s"""
        cu2.execute(q2, (handler[1],))
        stu_users = cu2.fetchall()
        cu2.close()

        return render_template('handler.html', handler=handler, subjects=subjects, tea_users=tea_users, stu_users=stu_users)


    
@app.route('/school/<int:handlerID>/<int:schoolID>/see_teachers', methods=['GET', 'POST'])
def all_teachers(handlerID, schoolID):
    cu1 = db.cursor()
    q1 = """SELECT u.*, t.* FROM users u join teacher t on u.userID = t.userID where u.schoolID = %s"""
    cu1.execute(q1, (schoolID, ))
    tea_users = cu1.fetchall()
    cu1.close()
    if request.method == 'POST':
               
        search_name = request.form['search_name']
        cu2 = db.cursor()
        q2 = """SELECT u.*, t.* FROM users u JOIN teacher t ON u.userID = t.userID
                WHERE u.schoolID = %s AND (u.name LIKE %s OR u.surname LIKE %s)"""
        cu2.execute(q2, (schoolID, f"%{search_name}%", f"%{search_name}%"))
        tea_users = cu2.fetchall()
        cu2.close()
        
    return render_template('show_teachers.html', handlerID=handlerID, tea_users=tea_users, schoolID = schoolID)


@app.route('/school/<int:handlerID>/<int:schoolID>/see_students', methods=['GET', 'POST'])
def all_students(handlerID, schoolID):
    cu1 = db.cursor()
    q1 = """SELECT u.*, t.* FROM users u join student t on u.userID = t.userID where u.schoolID = %s"""
    cu1.execute(q1, (schoolID, ))
    stu_users = cu1.fetchall()
    print(stu_users)
    cu1.close()
    if request.method == 'POST':
                
        search_name = request.form['search_name']
        cu2 = db.cursor()
        q2 = """SELECT u.*, t.* FROM users u JOIN student t ON u.userID = t.userID
                WHERE u.schoolID = %s AND (u.name LIKE %s OR u.surname LIKE %s)"""
        cu2.execute(q2, (schoolID, f"%{search_name}%", f"%{search_name}%"))
        stu_users = cu2.fetchall()
        cu2.close()
    return render_template('show_students.html', handlerID=handlerID, stu_users=stu_users, schoolID = schoolID)
  
    
@app.route('/school/student/<int:handlerID>/<int:userID>/loans')
def h_s_loans(handlerID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.loan_date, r.loanID, r.active, r.pending
        FROM loans AS r
        JOIN has_loan AS hs ON r.loanID = hs.loanID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        """

    cur.execute(query, (userID, ))
    stu_ln = cur.fetchall()
    cur.close()
    return render_template('h_s_loans.html', stu_ln = stu_ln, userID = userID)

@app.route('/school/teacher/<int:handlerID>/<int:userID>/loans')
def h_t_loans(handlerID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.loan_date, r.loanID, r.active, r.pending
        FROM loans AS r
        JOIN has_loan AS hs ON r.loanID = hs.loanID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        """

    cur.execute(query, (userID, ))
    tea_ln = cur.fetchall()
    cur.close()
    return render_template('h_t_loans.html', tea_ln = tea_ln, userID = userID)


@app.route('/school/student/<int:handlerID>/<int:userID>/reserv')
def h_s_res(handlerID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.res_date, r.resID, s.num_loans, b.available_copies
        FROM reservations AS r
        JOIN has_reserv AS hs ON r.resID = hs.resID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        JOIN student s on s.userID = %s
        where b.schoolID = (SELECT schoolID from users where userID = %s)
        """
    cur.execute(query, (userID, userID, userID))
    stu_rs = cur.fetchall()
    cur.close()
    
    cursor = db.cursor()
    current_date = date.today()
    print(date.today())
    seven_days_ago = current_date - timedelta(days=7)
    print(seven_days_ago)
    query = """
    SELECT loans.loan_date, loans.ISBN
    FROM loans
    JOIN has_loan ON loans.loanID = has_loan.loanID
    WHERE has_loan.userID = %s AND loans.loan_date < %s
    and loans.active = 1
    """
    cursor.execute(query, (userID, seven_days_ago))
    loans = cursor.fetchall()
    cn_ln = len(loans) == 0 
    cursor.close()

    return render_template('h_s_res.html', stu_rs = stu_rs, userID = userID, cn_ln = cn_ln)


@app.route('/school/teacher/<int:handlerID>/<int:userID>/reserv')
def h_t_res(handlerID, userID):
    cur = db.cursor()
    query = """
        SELECT DISTINCT r.ISBN, b.title, r.res_date, r.resID, s.num_loans, b.available_copies
        FROM reservations AS r
        JOIN has_reserv AS hs ON r.resID = hs.resID and hs.userID = %s
        JOIN books AS b ON b.ISBN = r.ISBN
        JOIN teacher s on s.userID = %s
        where b.schoolID = (SELECT schoolID from users where userID = %s)
        """
    cur.execute(query, (userID, userID, userID))
    tea_rs = cur.fetchall()
    cur.close()
    
    cursor = db.cursor()
    current_date = date.today()
    print(date.today())
    seven_days_ago = current_date - timedelta(days=7)
    print(seven_days_ago)
    query = """
    SELECT loans.loan_date, loans.ISBN
    FROM loans
    JOIN has_loan ON loans.loanID = has_loan.loanID
    WHERE has_loan.userID = %s AND datediff(current_date, loans.loan_date) > 7
    AND loans.active = 1
    """
    cursor.execute(query, (userID, ))
    loans = cursor.fetchall()
    cn_ln = len(loans) == 0 
    cursor.close()

    return render_template('h_t_res.html', tea_rs = tea_rs, userID = userID, cn_ln = cn_ln)

    
@app.route('/student/accept_loan/<int:userID>/<int:resID>/<int:ISBN>')
def acc_st_loan(userID, resID, ISBN):
    cur1 = db.cursor()
    q1 = """ 
    INSERT INTO loans values (default, %s, default, default, 1, 0)
    """
    cur1.execute(q1, (ISBN, ))
    db.commit()
    cur1.close()
    
    cur11 = db.cursor()
    q11 = """ 
    INSERT INTO has_loan (loanID, userID)
    SELECT MAX(loanID), %s
    FROM loans;
    """
    cur11.execute(q11, (userID, ))
    db.commit()
    cur11.close()
    
    cur3 = db.cursor()
    q3 = """ 
    SELECT schoolID FROM users where userID = %s
    """
    cur3.execute(q3, (userID, ))
    schoolID = cur3.fetchone()[0]
    cur3.close()
    
    cur2 = db.cursor()
    q2 = """ 
    UPDATE books SET available_copies = available_copies - 1 where ISBN = %s and schoolID = %s
    """
    cur2.execute(q2, (ISBN, schoolID))
    db.commit()
    cur2.close()
    
    cur4 = db.cursor()
    q4 = """ 
    UPDATE student SET num_loans = num_loans + 1, num_reserv = num_reserv - 1 where userID = %s
    """
    cur4.execute(q4, (userID, ))
    db.commit()
    cur4.close()
    
    cur5 = db.cursor()
    q5 = """
    DELETE FROM has_reserv WHERE userID = %s and resID = %s
    """
    cur5.execute(q5, (userID, resID))
    db.commit()
    cur5.close()
    
    cur6 = db.cursor()
    q6 = """
    DELETE FROM reservations WHERE  resID = %s
    """
    cur6.execute(q6, (resID,))
    db.commit()
    cur6.close()
    
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))


@app.route('/teacher/accept_loan/<int:userID>/<int:resID>/<int:ISBN>')
def acc_t_loan(userID, resID, ISBN):
    
    cur1 = db.cursor()
    q1 = """ 
    INSERT INTO loans values (default, %s, default, default, 1, 0)
    """
    cur1.execute(q1, (ISBN, ))
    db.commit()
    cur1.close()
    
    cur11 = db.cursor()
    q11 = """ 
    INSERT INTO has_loan (loanID, userID)
    SELECT MAX(loanID), %s
    FROM loans;
    """
    cur11.execute(q11, (userID, ))
    db.commit()
    cur11.close()
    
    cur3 = db.cursor()
    q3 = """ 
    SELECT schoolID FROM users where userID = %s
    """
    cur3.execute(q3, (userID, ))
    schoolID = cur3.fetchone()[0]
    cur3.close()
    
    cur2 = db.cursor()
    q2 = """ 
    UPDATE books SET available_copies = available_copies - 1 where ISBN = %s and schoolID = %s
    """
    cur2.execute(q2, (ISBN, schoolID))
    db.commit()
    cur2.close()
    
    cur4 = db.cursor()
    q4 = """ 
    UPDATE teacher SET num_loans = num_loans + 1, num_reserv = num_reserv - 1 where userID = %s
    """
    cur4.execute(q4, (userID, ))
    db.commit()
    cur4.close()
    
    cur5 = db.cursor()
    q5 = """
    DELETE FROM has_reserv WHERE userID = %s and resID = %s
    """
    cur5.execute(q5, (userID, resID))
    db.commit()
    cur5.close()
    
    cur6 = db.cursor()
    q6 = """
    DELETE FROM reservations WHERE  resID = %s
    """
    cur6.execute(q6, (resID,))
    db.commit()
    cur6.close()
    
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))


@app.route('/teacher/deactivate_loan/<int:userID>/<int:loanID>/<int:ISBN>')
def deact_t_loan(userID, loanID, ISBN):
    c1 = db.cursor()
    q1 = "UPDATE loans SET active = 0, end_date = default WHERE loanID = %s"
    c1.execute(q1, (loanID, ))
    db.commit()
    c1.close()
    
    cur4 = db.cursor()
    q4 = """ 
    UPDATE teacher SET num_loans = num_loans - 1 where userID = %s
    """
    cur4.execute(q4, (userID, ))
    db.commit()
    cur4.close()
    
    cur3 = db.cursor()
    q3 = """ 
    SELECT schoolID FROM users where userID = %s
    """
    cur3.execute(q3, (userID, ))
    schoolID = cur3.fetchone()[0]
    cur3.close()
    
    cur2 = db.cursor()
    q2 = """ 
    UPDATE books SET available_copies = available_copies + 1 where ISBN = %s and schoolID = %s
    """
    cur2.execute(q2, (ISBN, schoolID))
    db.commit()
    cur2.close()
    
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    
    
@app.route('/student/deactivate_loan/<int:userID>/<int:loanID>/<int:ISBN>')
def deact_s_loan(userID, loanID, ISBN):
    c1 = db.cursor()
    q1 = "UPDATE loans SET active = 0, end_date = default WHERE loanID = %s"
    c1.execute(q1, (loanID, ))
    db.commit()
    c1.close()
    
    cur4 = db.cursor()
    q4 = """ 
    UPDATE student SET num_loans = num_loans - 1 where userID = %s
    """
    cur4.execute(q4, (userID, ))
    db.commit()
    cur4.close()
    
    cur3 = db.cursor()
    q3 = """ 
    SELECT schoolID FROM users where userID = %s
    """
    cur3.execute(q3, (userID, ))
    schoolID = cur3.fetchone()[0]
    cur3.close()
    
    cur2 = db.cursor()
    q2 = """ 
    UPDATE books SET available_copies = available_copies + 1 where ISBN = %s and schoolID = %s
    """
    cur2.execute(q2, (ISBN, schoolID))
    db.commit()
    cur2.close()
    
    return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))


@app.route('/school/handler/modify_handler/<int:handlerID>', methods=['GET', 'POST'])
def modify_handler(handlerID):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        query = "UPDATE handler SET firstname = %s, lastname = %s, email = %s, password = %s WHERE handlerID = %s"
        cursor.execute(query, (name, surname, email, password, handlerID))
        db.commit()
        cursor.close()

        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        cursor = db.cursor()
        query = "SELECT * FROM handler WHERE handlerID = %s"
        cursor.execute(query, (handlerID,))
        handler = cursor.fetchone()
        cursor.close()
        return render_template('modify_handler.html', handler=handler)


@app.route('/query317')
def query317():
    cur = db.cursor()
    query = """
    SELECT a.authorID, a.name, COUNT(*) AS num_books
    FROM author a
    JOIN is_author isa ON a.authorID = isa.authorID
    GROUP BY a.authorID, a.name
    HAVING COUNT(*) + 4  < ( 
        SELECT COUNT(*) AS maxnum
    FROM author a1
    JOIN is_author a2 ON a1.authorID = a2.authorID
    GROUP BY a1.authorID, a1.name
    ORDER BY maxnum DESC
    LIMIT 1)
    """
    cur.execute(query)
    auths = cur.fetchall()
    cur.close()
    
    cur2 = db.cursor()
    q2 = """
    SELECT a1.name, COUNT(*) AS maxnum
    FROM author a1
    JOIN is_author a2 ON a1.authorID = a2.authorID
    GROUP BY a1.authorID, a1.name
    ORDER BY maxnum DESC
    LIMIT 1
    """
    cur2.execute(q2)
    auth1 = cur2.fetchone()
    cur2.close()
    
    return render_template('query317.html', auths = auths, auth1 = auth1)


@app.route('/query314')
def query314():
        c1 = db.cursor()
        q = """
         select a.name from author a
         except
         select distinct a.name from author a
         join is_author isa on isa.authorID = a.authorID
         join loans l on l.ISBN = isa.ISBN
        """
        c1.execute(q)
        auths = c1.fetchall()
        c1.close()
        print(auths)
        return render_template('query314.html', auths = auths)
    
    
@app.route('/<int:schoolID>/query323', methods=['GET', 'POST'])
def query323(schoolID):
    selected_subject_id = 'all'
    search_surname = ''

    if request.method == 'POST':
        selected_subject_id = request.form['subject_id']
        search_surname = request.form['search_surname']

        query = """
            select u.name, u.surname, avg(r.rating)
            from users u join review r on r.userID = u.userID
            join has_subject hs on hs.ISBN = r.ISBN
            where schoolID = %s
        """
        params = [schoolID]

        if selected_subject_id != 'all':
            query += "AND hs.subID = %s "
            params.append(selected_subject_id)

        if search_surname:
            query += "AND u.surname LIKE %s "
            params.append(f"%{search_surname}%")
        
        query += "group by u.userID "
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        revs = cursor.fetchall()
        cursor.close()
        print(revs)

    else:
        c1 = db.cursor()
        q = """
        select u.name, u.surname, avg(r.rating)
        from users u join review r on r.userID = u.userID
        where schoolID = %s
        group by u.userID
        """
        c1.execute(q, (schoolID, ))
        revs = c1.fetchall()
        c1.close()
    
    cu = db.cursor()
    query = """
        SELECT * FROM subjects
        """
    cu.execute(query)
    subjects = cu.fetchall()
    cu.close()
        
    return render_template('query323.html', revs = revs, subjects = subjects, selected_subject_id = selected_subject_id, search_surname = search_surname, schoolID = schoolID)
    
    
@app.route('/query313')
def query313():
    c1 = db.cursor()
    q1 = """
    SELECT user.name, user.surname, s.name , user.birthdate,  COUNT(*) as lns
    FROM users user
    JOIN teacher ON teacher.userID = user.userID
    Join has_loan hs on hs.userID = user.userID
    JOIN schools s on s.schoolID = user.schoolID
    WHERE TIMESTAMPDIFF(YEAR, user.birthdate, CURRENT_DATE) <= 40
    group by hs.userID
    HAVING lns = ( SELECT COUNT(*) as lns1
	FROM users u
	JOIN teacher ON teacher.userID = u.userID
	Join has_loan hs on hs.userID = u.userID
	WHERE TIMESTAMPDIFF(YEAR, user.birthdate, CURRENT_DATE) <= 40
	group by u.userID
	ORDER BY lns1 DESC LIMIT 1)
    ORDER BY lns DESC 
    """
    c1.execute(q1)
    maxloans = c1.fetchall()
    return render_template('query313.html', maxloans = maxloans)


@app.route('/query312', methods = ['GET', 'POST'])
def query312():
    selected_subject_id = 'all'
    if request.method == 'POST':
        selected_subject_id = request.form['subject_id']

        query1 = """
             select distinct a.name, a.name, 'Author' as entity_type from author a join is_author isa on isa.authorID = a.authorID
             join has_subject hs on hs.ISBN = isa.ISBN """
        
        query2 = """ union
             select u.name, u.surname, 'Teacher' as entity_type from users u
             join teacher t on t.userID = u.userID
             join has_loan hs on hs.userID = t.userID
             join loans l on l.loanID = hs.loanID 
             join has_subject hass on hass.ISBN = l.ISBN 
             WHERE DATEDIFF(current_date, l.loan_date) < 366
        """
        params = []

        if selected_subject_id != 'all':
            query1 += "WHERE hs.subID = %s "
            query2 += "AND hass.subID = %s "
            params.append(selected_subject_id)
            params.append(selected_subject_id)
            
        query = query1 + query2
        
        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        aut_tea = cursor.fetchall()
        cursor.close()

    else:
        c1 = db.cursor()
        q = """
         select distinct a.name, a.name, 'Author' as entity_type from author a join is_author isa on isa.authorID = a.authorID
         join has_subject hs on hs.ISBN = isa.ISBN 
         union
         select u.name, u.surname, 'Teacher' as entity_type from users u
         join teacher t on t.userID = u.userID
         join has_loan hs on hs.userID = t.userID
         join loans l on l.loanID = hs.loanID 
         join has_subject hass on hass.ISBN = l.ISBN 
         WHERE DATEDIFF(current_date, l.loan_date) < 366
        """
        c1.execute(q)
        aut_tea = c1.fetchall()
        c1.close()
    
    cu = db.cursor()
    query = """
        SELECT * FROM subjects
        """
    cu.execute(query)
    subjects = cu.fetchall()
    cu.close()
        
    return render_template('query312.html', aut_tea = aut_tea, subjects = subjects, selected_subject_id = selected_subject_id)
  

@app.route('/query315', methods=['POST','GET'])
def query315():
    if request.method == "POST":
        year = request.form['year']
        c = db.cursor()
        q = """
        SELECT DISTINCT h1.firstname, h1.lastname, h2.firstname, h2.lastname, s1.name, s2.name, counts.loan_count
FROM handler h1
JOIN schools s1 ON s1.schoolID = h1.schoolID
JOIN (
    SELECT COUNT(*) AS loan_count, u.schoolID
    FROM users u
    JOIN has_loan hl ON u.userID = hl.userID
	join loans l on l.loanID = hl.loanID
	WHERE year(l.loan_date) = %s
    GROUP BY u.schoolID
    HAVING COUNT(*) > 20
) AS counts ON s1.schoolID = counts.schoolID
JOIN schools s2 ON s2.schoolID != s1.schoolID
JOIN handler h2 ON h2.schoolID = s2.schoolID
JOIN (
    SELECT COUNT(*) AS loan_count, u.schoolID
    FROM users u
    JOIN has_loan hl ON u.userID = hl.userID
	join loans l on l.loanID = hl.loanID
	WHERE year(l.loan_date) = %s 
    GROUP BY u.schoolID
) AS counts2 ON counts2.schoolID = s2.schoolID AND counts2.loan_count = counts.loan_count 
WHERE h2.handlerID > h1.handlerID and h1.active * h2.active > 0
GROUP BY h1.handlerID, h2.handlerID
        """
        c.execute(q, (int(year), int(year)))
        handls = c.fetchall()
        c.close()
        t = True
        return render_template('query315.html', t=t, handls = handls)
    else:
        t = False
        return render_template('query315.html', t=t)

@app.route('/query316')
def query316():
    c = db.cursor()
    q = """
    SELECT s1.subject AS subject1, s2.subject AS subject2, COUNT(*) AS loan_count
    FROM has_subject hs1
    JOIN has_subject hs2 ON hs1.ISBN = hs2.ISBN AND hs1.subID < hs2.subID
    JOIN subjects s1 ON hs1.subID = s1.subID
    JOIN subjects s2 ON hs2.subID = s2.subID
    JOIN loans hl ON hl.ISBN = hs1.ISBN
    GROUP BY hs1.subID, hs2.subID
    ORDER BY loan_count DESC
    LIMIT 3
    """
    c.execute(q)
    couples = c.fetchall()
    return render_template('query316.html', couples = couples)


@app.route('/school/<int:school_id>/all_loans', methods=['GET', 'POST'])
def all_loans(school_id):
        cursor = db.cursor()
        cursor.execute("""
            select u.name, u.surname, l.ISBN, l.loan_date, l.active, datediff(current_date, l.loan_date) from users u
            join has_loan hs on hs.userID = u.userID
            join loans l on l.loanID = hs.loanID
            AND u.schoolID = %s
        """, (school_id,))
        res = cursor.fetchall()
        cursor.close()
        print(res)
    
        return render_template('all_loans.html', school_id=school_id, res = res)


@app.route('/school/<int:school_id>/all_res', methods=['GET', 'POST'])
def all_res(school_id):
        cursor = db.cursor()
        cursor.execute("""
            select u.name, u.surname, l.ISBN, l.res_date from users u
            join has_reserv hs on hs.userID = u.userID
            join reservations l on l.resID = hs.resID
            AND u.schoolID = %s
        """, (school_id,))
        res = cursor.fetchall()
        cursor.close()
        print(res)
    
        return render_template('all_res.html', school_id=school_id, res = res)


@app.route('/school/<int:school_id>/loans_delayed', methods=['GET', 'POST'])
def delayed_loans(school_id):
    search_name = ''
    search_surname = ''
    search_date = ''

    if request.method == 'POST':
        search_name = request.form['search_name']
        search_author = request.form['search_surname']
        search_date = request.form['search_date']

        query = """
            select u.name, u.surname, l.ISBN, l.loan_date from users u
            join has_loan hs on hs.userID = u.userID
            join loans l on l.loanID = hs.loanID
            where l.active = 1
            AND u.schoolID = %s
        """
        params = [school_id]


        if search_name:
            query += "AND u.name LIKE %s "
            params.append(f"%{search_name}%")

        if search_surname:
            query += "AND u.surname LIKE %s "
            params.append(f"%{search_surname}%")

        if search_date:
            query += "AND DATEDIFF(CURRENT_DATE, l.loan_date) >= 7 + %s "
            params.append(int(search_date))
        else :
            query += "AND DATEDIFF(CURRENT_DATE, l.loan_date) >= 7 "

        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        res = cursor.fetchall()
        cursor.close()
        print(res)

    else:
        cursor = db.cursor()
        cursor.execute("""
            select u.name, u.surname, l.ISBN, l.loan_date from users u
            join has_loan hs on hs.userID = u.userID
            join loans l on l.loanID = hs.loanID
            where l.active = 1 AND DATEDIFF(CURRENT_DATE, l.loan_date) >= 7 
            AND u.schoolID = %s
        """, (school_id,))
        res = cursor.fetchall()
        cursor.close()
        print(res)
    
    return render_template('delayed_loans.html', school_id=school_id, res = res, search_name=search_name, search_surname=search_surname, search_date=search_date)


@app.route('/new_school', methods=['GET', 'POST'])
def new_school():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        str_name = request.form['str_name']
        str_number = request.form['str_number']
        zip_code = request.form['zip_code']
        city = request.form['city']
        d_name = request.form['d_name']
        d_surname = request.form['d_surname']
        d_email = request.form['d_email']
        d_username = request.form['d_username']
        d_password = request.form['d_password']
        d_date = request.form['d_date']
        print(request.form)
        
        cursor = db.cursor()
        query = """ INSERT INTO schools (schoolID, name, email, phone, str_name, str_number, zip_code, city)
        VALUES (default, %s, %s, %s, %s, %s, %s, %s )"""
        cursor.execute(query, (name, email, phone, str_name, str_number, zip_code, city))
        db.commit()
        cursor.close()
        
        cursor1 = db.cursor()
        query1 = """ SELECT schoolID FROM schools ORDER BY schoolID DESC LIMIT 1"""
        cursor1.execute(query1)
        schoolID = cursor1.fetchone()[0]
        db.commit()
        cursor1.close()
        
        cursor2 = db.cursor()
        query2 = """ INSERT INTO users VALUES (default, %s, %s, %s, %s, %s, %s, 1, %s)"""
        cursor2.execute(query2, (schoolID, d_name, d_surname, d_email, d_username, d_password, d_date))
        db.commit()
        cursor2.close()
        
        cursor1 = db.cursor()
        query1 = """ SELECT userID FROM users ORDER BY userID DESC LIMIT 1"""
        cursor1.execute(query1)
        userID = cursor1.fetchone()[0]
        db.commit()
        cursor1.close()
        
        cursor2 = db.cursor()
        query2 = """ INSERT INTO school_director VALUES (default, %s, %s, %s, %s)"""
        cursor2.execute(query2, (schoolID, d_name, d_surname, userID))
        db.commit()
        cursor2.close()
        
        cursor2 = db.cursor()
        query2 = """ INSERT INTO teacher(userID) VALUES (%s)"""
        cursor2.execute(query2, (userID,))
        db.commit()
        cursor2.close()
        
        return redirect(url_for('welcome',  message='Επιτυχής Καταχώρηση'))
    else:
        return render_template('new_school.html')



@app.route('/<int:schoolID>/<int:userID>/book_by_title', methods=['GET', 'POST'])
def book_by_title(schoolID, userID):
    if request.method == 'POST':
        title = request.form['title']
        c = db.cursor()
        query = """
            SELECT b.ISBN, b.schoolID, b.title, b.available_copies
            FROM books b
            WHERE b.schoolID = %s AND b.title LIKE %s;
        """
        c.execute(query, (schoolID, f"%{title}%"))
        books = c.fetchall()
        c.close()
        return redirect(f"/search_results?title={title}")
    return render_template('book_search.html')


@app.route('/search_results')
def search_results():
    title = request.args.get('title')
    return render_template('search_results.html', title=title)



if __name__ == '__main__':
    app.run()
