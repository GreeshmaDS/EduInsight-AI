import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

students = [

("S1001","Aarav","Male","Science",95,7,85,90,92,"PASS ✅",98.2,"A+"),
("S1002","Ananya","Female","Commerce",88,6,80,82,85,"PASS ✅",96.4,"A"),
("S1003","Rahul","Male","Arts",75,4,70,72,68,"PASS ✅",88.5,"B"),
("S1004","Priya","Female","Management",92,8,90,88,95,"PASS ✅",99.1,"A+"),
("S1005","Arjun","Male","Science",80,5,72,75,78,"PASS ✅",91.7,"B"),
("S1006","Sneha","Female","Commerce",85,6,78,80,82,"PASS ✅",94.2,"A"),
("S1007","Kiran","Male","Management",70,3,60,65,58,"FAIL ❌",76.8,"D"),
("S1008","Divya","Female","Arts",90,7,88,86,90,"PASS ✅",98.0,"A+"),
("S1009","Rohit","Male","Science",65,2,55,60,52,"FAIL ❌",72.5,"D"),
("S1010","Meera","Female","Commerce",96,9,94,96,98,"PASS ✅",99.6,"A+")

]

for s in students:
    cursor.execute("""
    INSERT INTO students(
        studentid,
        studentname,
        gender,
        department,
        attendance,
        studyhours,
        internalmarks,
        assignmentmarks,
        finalexammarks,
        prediction,
        confidence,
        grade
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """, s)

conn.commit()
conn.close()

print("Students added successfully!")