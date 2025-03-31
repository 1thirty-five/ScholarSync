import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

# -----------------------------
# Database Setup using SQLite
# -----------------------------
conn = sqlite3.connect("student_grades.db")
cursor = conn.cursor()

def init_db():
    cursor.execute('''CREATE TABLE IF NOT EXISTS Student (
                        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Course (
                        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        course_name TEXT NOT NULL UNIQUE,
                        credits INTEGER NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Grade (
                        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        course_id INTEGER NOT NULL,
                        semester INTEGER NOT NULL,
                        grade_point REAL NOT NULL,
                        FOREIGN KEY (student_id) REFERENCES Student(student_id),
                        FOREIGN KEY (course_id) REFERENCES Course(course_id))''')
    conn.commit()

init_db()

# -----------------------------
# Tkinter GUI Application
# -----------------------------
root = tk.Tk()
root.title("CGPA Calculator System")
root.geometry("900x600")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# -------------
# Student Tab
# -------------
student_frame = ttk.Frame(notebook)
notebook.add(student_frame, text="Students")

student_tree = ttk.Treeview(student_frame, columns=("ID", "Name", "Email"), show="headings")
for col in ("ID", "Name", "Email"):
    student_tree.heading(col, text=col)
student_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_student_tree():
    for row in student_tree.get_children():
        student_tree.delete(row)
    cursor.execute("SELECT * FROM Student")
    for row in cursor.fetchall():
        student_tree.insert("", "end", values=row)

def add_student():
    popup = tk.Toplevel(root)
    popup.title("Add Student")

    tk.Label(popup, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(popup)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(popup, text="Email:").grid(row=1, column=0, padx=5, pady=5)
    email_entry = tk.Entry(popup)
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        name = name_entry.get()
        email = email_entry.get()
        if name and email:
            try:
                cursor.execute("INSERT INTO Student (name, email) VALUES (?, ?)", 
                               (name, email))
                conn.commit()
                refresh_student_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not add student: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    tk.Button(popup, text="Add", command=submit).grid(row=3, column=0, columnspan=2, pady=10)

def update_student():
    selected = student_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to update.")
        return
    record = student_tree.item(selected, "values")
    student_id = record[0]
    
    popup = tk.Toplevel(root)
    popup.title("Update Student")
    
    tk.Label(popup, text="Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(popup)
    name_entry.insert(0, record[1])
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(popup, text="Email:").grid(row=1, column=0, padx=5, pady=5)
    email_entry = tk.Entry(popup)
    email_entry.insert(0, record[2])
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        name = name_entry.get()
        email = email_entry.get()
        if name and email:
            try:
                cursor.execute("UPDATE Student SET name=?, email=? WHERE student_id=?",
                               (name, email, student_id))
                conn.commit()
                refresh_student_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not update student: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    tk.Button(popup, text="Update", command=submit).grid(row=3, column=0, columnspan=2, pady=10)

def delete_student():
    selected = student_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to delete.")
        return
    record = student_tree.item(selected, "values")
    student_id = record[0]
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
        cursor.execute("DELETE FROM Student WHERE student_id=?", (student_id,))
        conn.commit()
        refresh_student_tree()

# Buttons for Student Tab
student_button_frame = ttk.Frame(student_frame)
student_button_frame.pack(pady=5)

ttk.Button(student_button_frame, text="Add Student", command=add_student).pack(side="left", padx=5)
ttk.Button(student_button_frame, text="Update Student", command=update_student).pack(side="left", padx=5)
ttk.Button(student_button_frame, text="Delete Student", command=delete_student).pack(side="left", padx=5)

refresh_student_tree()

# -------------
# Course Tab
# -------------
course_frame = ttk.Frame(notebook)
notebook.add(course_frame, text="Courses")

course_tree = ttk.Treeview(course_frame, columns=("ID", "Course Name", "Credits"), show="headings")
course_tree.heading("ID", text="ID")
course_tree.heading("Course Name", text="Course Name")
course_tree.heading("Credits", text="Credits")
course_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_course_tree():
    for row in course_tree.get_children():
        course_tree.delete(row)
    cursor.execute("SELECT * FROM Course")
    for row in cursor.fetchall():
        course_tree.insert("", "end", values=row)

def add_course():
    popup = tk.Toplevel(root)
    popup.title("Add Course")

    tk.Label(popup, text="Course Name:").grid(row=0, column=0, padx=5, pady=5)
    course_entry = tk.Entry(popup)
    course_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Credits:").grid(row=1, column=0, padx=5, pady=5)
    credits_entry = tk.Entry(popup)
    credits_entry.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        course_name = course_entry.get()
        credits = credits_entry.get()
        if course_name and credits:
            try:
                cursor.execute("INSERT INTO Course (course_name, credits) VALUES (?, ?)", 
                               (course_name, int(credits)))
                conn.commit()
                refresh_course_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not add course: {e}")
            except ValueError:
                messagebox.showwarning("Input Error", "Credits must be a number.")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    tk.Button(popup, text="Add", command=submit).grid(row=2, column=0, columnspan=2, pady=10)

def update_course():
    selected = course_tree.focus()
    if not selected:
        messagebox.showwarning("Select Course", "Please select a course to update.")
        return
    record = course_tree.item(selected, "values")
    course_id = record[0]
    
    popup = tk.Toplevel(root)
    popup.title("Update Course")
    
    tk.Label(popup, text="Course Name:").grid(row=0, column=0, padx=5, pady=5)
    course_entry = tk.Entry(popup)
    course_entry.insert(0, record[1])
    course_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Credits:").grid(row=1, column=0, padx=5, pady=5)
    credits_entry = tk.Entry(popup)
    credits_entry.insert(0, record[2])
    credits_entry.grid(row=1, column=1, padx=5, pady=5)

    def submit():
        course_name = course_entry.get()
        credits = credits_entry.get()
        if course_name and credits:
            try:
                cursor.execute("UPDATE Course SET course_name=?, credits=? WHERE course_id=?",
                               (course_name, int(credits), course_id))
                conn.commit()
                refresh_course_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not update course: {e}")
            except ValueError:
                messagebox.showwarning("Input Error", "Credits must be a number.")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    tk.Button(popup, text="Update", command=submit).grid(row=2, column=0, columnspan=2, pady=10)

def delete_course():
    selected = course_tree.focus()
    if not selected:
        messagebox.showwarning("Select Course", "Please select a course to delete.")
        return
    record = course_tree.item(selected, "values")
    course_id = record[0]
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this course?"):
        cursor.execute("DELETE FROM Course WHERE course_id=?", (course_id,))
        conn.commit()
        refresh_course_tree()

# Buttons for Course Tab
course_button_frame = ttk.Frame(course_frame)
course_button_frame.pack(pady=5)

ttk.Button(course_button_frame, text="Add Course", command=add_course).pack(side="left", padx=5)
ttk.Button(course_button_frame, text="Update Course", command=update_course).pack(side="left", padx=5)
ttk.Button(course_button_frame, text="Delete Course", command=delete_course).pack(side="left", padx=5)

refresh_course_tree()

# -------------
# Grade Tab
# -------------
grade_frame = ttk.Frame(notebook)
notebook.add(grade_frame, text="Grades")

grade_tree = ttk.Treeview(grade_frame, columns=("ID", "Student", "Course", "Semester", "Grade Point"), show="headings")
for col in ("ID", "Student", "Course", "Semester", "Grade Point"):
    grade_tree.heading(col, text=col)
grade_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_grade_tree():
    for row in grade_tree.get_children():
        grade_tree.delete(row)
    cursor.execute("""
        SELECT g.grade_id, s.name, c.course_name, g.semester, g.grade_point 
        FROM Grade g 
        JOIN Student s ON g.student_id = s.student_id 
        JOIN Course c ON g.course_id = c.course_id
    """)
    for row in cursor.fetchall():
        grade_tree.insert("", "end", values=row)

def add_grade():
    popup = tk.Toplevel(root)
    popup.title("Add Grade")

    # Get lists of students and courses for selection
    cursor.execute("SELECT student_id, name FROM Student")
    students = cursor.fetchall()
    cursor.execute("SELECT course_id, course_name FROM Course")
    courses = cursor.fetchall()
    
    tk.Label(popup, text="Student:").grid(row=0, column=0, padx=5, pady=5)
    student_var = tk.StringVar()
    student_choices = {f"{sid} - {name}": sid for sid, name in students}
    student_menu = ttk.Combobox(popup, textvariable=student_var, values=list(student_choices.keys()), state="readonly")
    student_menu.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Course:").grid(row=1, column=0, padx=5, pady=5)
    course_var = tk.StringVar()
    course_choices = {f"{cid} - {course}": cid for cid, course in courses}
    course_menu = ttk.Combobox(popup, textvariable=course_var, values=list(course_choices.keys()), state="readonly")
    course_menu.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Semester:").grid(row=2, column=0, padx=5, pady=5)
    semester_entry = tk.Entry(popup)
    semester_entry.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Grade Point:").grid(row=3, column=0, padx=5, pady=5)
    grade_entry = tk.Entry(popup)
    grade_entry.grid(row=3, column=1, padx=5, pady=5)
    
    def submit():
        stud_key = student_var.get()
        course_key = course_var.get()
        semester = semester_entry.get()
        grade_point = grade_entry.get()
        if stud_key and course_key and semester and grade_point:
            try:
                student_id = student_choices[stud_key]
                course_id = course_choices[course_key]
                cursor.execute("INSERT INTO Grade (student_id, course_id, semester, grade_point) VALUES (?, ?, ?, ?)",
                               (student_id, course_id, int(semester), float(grade_point)))
                conn.commit()
                refresh_grade_tree()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add grade: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")
    
    tk.Button(popup, text="Add", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

def update_grade():
    selected = grade_tree.focus()
    if not selected:
        messagebox.showwarning("Select Grade", "Please select a grade to update.")
        return
    record = grade_tree.item(selected, "values")
    grade_id = record[0]
    
    # Get current grade details
    cursor.execute("""
        SELECT g.student_id, g.course_id, g.semester, g.grade_point, s.name, c.course_name 
        FROM Grade g 
        JOIN Student s ON g.student_id = s.student_id 
        JOIN Course c ON g.course_id = c.course_id 
        WHERE g.grade_id = ?
    """, (grade_id,))
    grade_data = cursor.fetchone()
    
    popup = tk.Toplevel(root)
    popup.title("Update Grade")
    
    # Get lists of students and courses for selection
    cursor.execute("SELECT student_id, name FROM Student")
    students = cursor.fetchall()
    cursor.execute("SELECT course_id, course_name FROM Course")
    courses = cursor.fetchall()
    
    tk.Label(popup, text="Student:").grid(row=0, column=0, padx=5, pady=5)
    student_var = tk.StringVar()
    student_choices = {f"{sid} - {name}": sid for sid, name in students}
    student_menu = ttk.Combobox(popup, textvariable=student_var, values=list(student_choices.keys()), state="readonly")
    student_menu.set(f"{grade_data[0]} - {grade_data[4]}")
    student_menu.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Course:").grid(row=1, column=0, padx=5, pady=5)
    course_var = tk.StringVar()
    course_choices = {f"{cid} - {course}": cid for cid, course in courses}
    course_menu = ttk.Combobox(popup, textvariable=course_var, values=list(course_choices.keys()), state="readonly")
    course_menu.set(f"{grade_data[1]} - {grade_data[5]}")
    course_menu.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Semester:").grid(row=2, column=0, padx=5, pady=5)
    semester_entry = tk.Entry(popup)
    semester_entry.insert(0, grade_data[2])
    semester_entry.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Grade Point:").grid(row=3, column=0, padx=5, pady=5)
    grade_entry = tk.Entry(popup)
    grade_entry.insert(0, grade_data[3])
    grade_entry.grid(row=3, column=1, padx=5, pady=5)
    
    def submit():
        stud_key = student_var.get()
        course_key = course_var.get()
        semester = semester_entry.get()
        grade_point = grade_entry.get()
        if stud_key and course_key and semester and grade_point:
            try:
                student_id = student_choices[stud_key]
                course_id = course_choices[course_key]
                cursor.execute("UPDATE Grade SET student_id=?, course_id=?, semester=?, grade_point=? WHERE grade_id=?",
                               (student_id, course_id, int(semester), float(grade_point), grade_id))
                conn.commit()
                refresh_grade_tree()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update grade: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")
    
    tk.Button(popup, text="Update", command=submit).grid(row=4, column=0, columnspan=2, pady=10, bg="#fff")
def delete_grade():
    selected = grade_tree.focus()
    if not selected:
        messagebox.showwarning("Select Grade", "Please select a grade to delete.")
        return
    record = grade_tree.item(selected, "values")
    grade_id = record[0]
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this grade?"):
        cursor.execute("DELETE FROM Grade WHERE grade_id=?", (grade_id,))
        conn.commit()
        refresh_grade_tree()

# Buttons for Grade Tab
grade_button_frame = ttk.Frame(grade_frame)
grade_button_frame.pack(pady=5)

ttk.Button(grade_button_frame, text="Add Grade", command=add_grade).pack(side="left", padx=5)
ttk.Button(grade_button_frame, text="Update Grade", command=update_grade).pack(side="left", padx=5)
ttk.Button(grade_button_frame, text="Delete Grade", command=delete_grade).pack(side="left", padx=5)

refresh_grade_tree()

# -------------
# CGPA Calculator Tab
# -------------
calculator_frame = ttk.Frame(notebook)
notebook.add(calculator_frame, text="CGPA Calculator")

# Top part: Student Selection
calc_top_frame = ttk.Frame(calculator_frame)
calc_top_frame.pack(fill="x", padx=10, pady=10)

tk.Label(calc_top_frame, text="Select Student:").pack(side="left", padx=5)
student_var = tk.StringVar()
cursor.execute("SELECT student_id, name FROM Student")
students = cursor.fetchall()
student_choices = {f"{sid} - {name}": sid for sid, name in students}
student_menu = ttk.Combobox(calc_top_frame, textvariable=student_var, 
                        values=list(student_choices.keys()), width=30, state="readonly")
student_menu.pack(side="left", padx=5)

# Middle part: Results Display
results_frame = ttk.LabelFrame(calculator_frame, text="GPA Results")
results_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Create a treeview for semester-wise SGPA
sgpa_tree = ttk.Treeview(results_frame, columns=("Semester", "SGPA", "Credits"), show="headings")
sgpa_tree.heading("Semester", text="Semester")
sgpa_tree.heading("SGPA", text="SGPA")
sgpa_tree.heading("Credits", text="Credits")
sgpa_tree.pack(fill="both", expand=True, padx=10, pady=10)

# CGPA Display
cgpa_frame = ttk.Frame(results_frame)
cgpa_frame.pack(fill="x", padx=10, pady=5)

cgpa_label = tk.Label(cgpa_frame, text="CGPA: ", font=("Arial", 14, "bold"))
cgpa_label.pack(side="left")

cgpa_value = tk.Label(cgpa_frame, text="--", font=("Arial", 14))
cgpa_value.pack(side="left")

total_credits_label = tk.Label(cgpa_frame, text="Total Credits: ", font=("Arial", 12), padx=20)
total_credits_label.pack(side="left")

total_credits_value = tk.Label(cgpa_frame, text="--", font=("Arial", 12))
total_credits_value.pack(side="left")

def calculate_cgpa():
    # Clear previous results
    for row in sgpa_tree.get_children():
        sgpa_tree.delete(row)
    
    student_selection = student_var.get()
    if not student_selection:
        messagebox.showwarning("Selection Error", "Please select a student.")
        return
    
    student_id = student_choices[student_selection]
    
    # Get all semesters for this student
    cursor.execute("SELECT DISTINCT semester FROM Grade WHERE student_id = ? ORDER BY semester", (student_id,))
    semesters = [row[0] for row in cursor.fetchall()]
    
    if not semesters:
        messagebox.showinfo("No Data", "No grade data found for this student.")
        cgpa_value.config(text="--")
        total_credits_value.config(text="--")
        return
    
    # Calculate SGPA for each semester
    semester_credits = []
    semester_sgpas = []
    
    for semester in semesters:
        cursor.execute("""
            SELECT g.grade_point, c.credits 
            FROM Grade g 
            JOIN Course c ON g.course_id = c.course_id 
            WHERE g.student_id = ? AND g.semester = ?
        """, (student_id, semester))
        grades = cursor.fetchall()
        
        total_points = sum(grade * credits for grade, credits in grades)
        total_credits = sum(credits for _, credits in grades)
        
        if total_credits > 0:
            sgpa = total_points / total_credits
            semester_credits.append(total_credits)
            semester_sgpas.append(sgpa)
            sgpa_tree.insert("", "end", values=(f"Semester {semester}", f"{sgpa:.2f}", total_credits))
    
    # Calculate CGPA using the formula from the image
    total_weighted_sgpa = sum(sgpa * credits for sgpa, credits in zip(semester_sgpas, semester_credits))
    total_all_credits = sum(semester_credits)
    
    if total_all_credits > 0:
        cgpa = total_weighted_sgpa / total_all_credits
        cgpa_value.config(text=f"{cgpa:.2f}")
        total_credits_value.config(text=f"{total_all_credits}")
    else:
        cgpa_value.config(text="--")
        total_credits_value.config(text="--")

# Button to calculate
calc_button_frame = ttk.Frame(calculator_frame)
calc_button_frame.pack(pady=10)

ttk.Button(calc_button_frame, text="Calculate CGPA", command=calculate_cgpa).pack()

# Formula display
formula_frame = ttk.LabelFrame(calculator_frame, text="Formula Reference")
formula_frame.pack(fill="x", padx=10, pady=10)

formula_text = """
SGPA Formula: SGPA = Σ(Credits × Grade Points) / Σ(Credits)
CGPA Formula: CGPA = Σ(Credits × SGPA) / Σ(Credits)

Where:
- Credits: Number of credit hours for each course
- Grade Points: Points scored in each course (usually on a scale of 0-4 or 0-10)
- SGPA: Semester Grade Point Average
- CGPA: Cumulative Grade Point Average
"""
tk.Label(formula_frame, text=formula_text, justify="left").pack(padx=10, pady=10)

# -----------------------------
# Main loop
# -----------------------------
root.mainloop()

# Close the database connection when the app exits
conn.close()