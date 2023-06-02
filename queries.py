#query 3.1.1
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


#query 3.1.2

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

query = query1 + query2 # τελικό query

#query 3.1.3

"""
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

#query 3.1.4

"""
select a.name from author a
         except
         select distinct a.name from author a
         join is_author isa on isa.authorID = a.authorID
         join loans l on l.ISBN = isa.ISBN
"""

#query 3.1.5

"""
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

#query 3.1.6

"""
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

#query 3.1.7

"""
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


#query 3.2.1

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


#query 3.2.2

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


#query 3.2.3

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


#query 3.3.1

#λίστα βιβλίων

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


#query 3.3.2

"""
SELECT DISTINCT r.ISBN, b.title, r.loan_date, r.loanID, r.active, r.pending
FROM loans AS r
JOIN has_loan AS hs ON r.loanID = hs.loanID and hs.userID = %s
JOIN books AS b ON b.ISBN = r.ISBN
"""
