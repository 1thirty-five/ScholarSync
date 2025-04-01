import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import os
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
root.title("ScholarSync")
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

course_tree = ttk.Treeview(course_frame, columns=("ID", "Course Name", "Credits", "Professor"), show="headings")
course_tree.heading("ID", text="ID")
course_tree.heading("Course Name", text="Course Name")
course_tree.heading("Credits", text="Credits")
course_tree.heading("Professor", text="Professor")
course_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_course_tree():
    for row in course_tree.get_children():
        course_tree.delete(row)
    cursor.execute("""
        SELECT c.course_id, c.course_name, c.credits, 
               IFNULL(p.last_name || ', ' || p.first_name, 'Not Assigned') as professor_name
        FROM Course c
        LEFT JOIN CourseAssignment ca ON c.course_id = ca.course_id
        LEFT JOIN Professor p ON ca.professor_id = p.professor_id
    """)
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
    
    tk.Label(popup, text="Professor:").grid(row=2, column=0, padx=5, pady=5)
    
    # Get all professors for dropdown
    cursor.execute("SELECT professor_id, first_name || ' ' || last_name as full_name FROM Professor ORDER BY last_name, first_name")
    professors = [("", "-- Select Professor --")] + [(str(row[0]), row[1]) for row in cursor.fetchall()]
    
    professor_var = tk.StringVar()
    professor_dropdown = ttk.Combobox(popup, textvariable=professor_var, state="readonly")
    professor_dropdown['values'] = [prof[1] for prof in professors]
    professor_dropdown.current(0)
    professor_dropdown.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        course_name = course_entry.get()
        credits = credits_entry.get()
        selected_prof_index = professor_dropdown.current()
        
        if course_name and credits:
            try:
                # First, insert the course
                cursor.execute("INSERT INTO Course (course_name, credits) VALUES (?, ?)", 
                               (course_name, int(credits)))
                course_id = cursor.lastrowid
                
                # Then, if a professor was selected, create the assignment
                if selected_prof_index > 0:  # Skip the "-- Select Professor --" option
                    professor_id = professors[selected_prof_index][0]
                    cursor.execute("INSERT INTO CourseAssignment (course_id, professor_id) VALUES (?, ?)",
                                  (course_id, professor_id))
                
                conn.commit()
                refresh_course_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not add course: {e}")
            except ValueError:
                messagebox.showwarning("Input Error", "Credits must be a number.")
        else:
            messagebox.showwarning("Input Error", "Course name and credits are required.")

    tk.Button(popup, text="Add", command=submit).grid(row=3, column=0, columnspan=2, pady=10)

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
    
    tk.Label(popup, text="Professor:").grid(row=2, column=0, padx=5, pady=5)
    
    # Get all professors for dropdown
    cursor.execute("SELECT professor_id, first_name || ' ' || last_name as full_name FROM Professor ORDER BY last_name, first_name")
    professors = [("", "-- Select Professor --")] + [(str(row[0]), row[1]) for row in cursor.fetchall()]
    
    professor_var = tk.StringVar()
    professor_dropdown = ttk.Combobox(popup, textvariable=professor_var, state="readonly")
    professor_dropdown['values'] = [prof[1] for prof in professors]
    
    # Get current professor for this course
    cursor.execute("""
        SELECT p.professor_id, p.first_name || ' ' || p.last_name as full_name
        FROM Professor p
        JOIN CourseAssignment ca ON p.professor_id = ca.professor_id
        WHERE ca.course_id = ?
    """, (course_id,))
    current_prof = cursor.fetchone()
    
    # Set current selection in dropdown
    if current_prof:
        for i, prof in enumerate(professors):
            if prof[0] == str(current_prof[0]):
                professor_dropdown.current(i)
                break
    else:
        professor_dropdown.current(0)  # No professor assigned
        
    professor_dropdown.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        course_name = course_entry.get()
        credits = credits_entry.get()
        selected_prof_index = professor_dropdown.current()
        
        if course_name and credits:
            try:
                # First, update the course
                cursor.execute("UPDATE Course SET course_name=?, credits=? WHERE course_id=?",
                               (course_name, int(credits), course_id))
                
                # Then, update the professor assignment
                cursor.execute("DELETE FROM CourseAssignment WHERE course_id=?", (course_id,))
                
                if selected_prof_index > 0:  # Skip the "-- Select Professor --" option
                    professor_id = professors[selected_prof_index][0]
                    cursor.execute("INSERT INTO CourseAssignment (course_id, professor_id) VALUES (?, ?)",
                                  (course_id, professor_id))
                
                conn.commit()
                refresh_course_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not update course: {e}")
            except ValueError:
                messagebox.showwarning("Input Error", "Credits must be a number.")
        else:
            messagebox.showwarning("Input Error", "Course name and credits are required.")

    tk.Button(popup, text="Update", command=submit).grid(row=3, column=0, columnspan=2, pady=10)

def delete_course():
    selected = course_tree.focus()
    if not selected:
        messagebox.showwarning("Select Course", "Please select a course to delete.")
        return
    record = course_tree.item(selected, "values")
    course_id = record[0]
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this course?"):
        # Delete from CourseAssignment first due to foreign key constraints
        cursor.execute("DELETE FROM CourseAssignment WHERE course_id=?", (course_id,))
        cursor.execute("DELETE FROM Course WHERE course_id=?", (course_id,))
        conn.commit()
        refresh_course_tree()

# Buttons for Course Tab
course_button_frame = ttk.Frame(course_frame)
course_button_frame.pack(pady=5)

ttk.Button(course_button_frame, text="Add Course", command=add_course).pack(side="left", padx=5)
ttk.Button(course_button_frame, text="Update Course", command=update_course).pack(side="left", padx=5)
ttk.Button(course_button_frame, text="Delete Course", command=delete_course).pack(side="left", padx=5)

# -------------
# Professor Tab
# -------------
professor_frame = ttk.Frame(notebook)
notebook.add(professor_frame, text="Professors")

professor_tree = ttk.Treeview(professor_frame, columns=("ID", "First Name", "Last Name", "Department", "Email"), show="headings")
professor_tree.heading("ID", text="ID")
professor_tree.heading("First Name", text="First Name")
professor_tree.heading("Last Name", text="Last Name")
professor_tree.heading("Department", text="Department")
professor_tree.heading("Email", text="Email")
professor_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_professor_tree():
    for row in professor_tree.get_children():
        professor_tree.delete(row)
    cursor.execute("SELECT * FROM Professor")
    for row in cursor.fetchall():
        professor_tree.insert("", "end", values=row)

def add_professor():
    popup = tk.Toplevel(root)
    popup.title("Add Professor")

    tk.Label(popup, text="First Name:").grid(row=0, column=0, padx=5, pady=5)
    first_name_entry = tk.Entry(popup)
    first_name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Last Name:").grid(row=1, column=0, padx=5, pady=5)
    last_name_entry = tk.Entry(popup)
    last_name_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Department:").grid(row=2, column=0, padx=5, pady=5)
    department_entry = tk.Entry(popup)
    department_entry.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Email:").grid(row=3, column=0, padx=5, pady=5)
    email_entry = tk.Entry(popup)
    email_entry.grid(row=3, column=1, padx=5, pady=5)

    def submit():
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        department = department_entry.get()
        email = email_entry.get()
        
        if first_name and last_name and department and email:
            try:
                cursor.execute("INSERT INTO Professor (first_name, last_name, department, email) VALUES (?, ?, ?, ?)", 
                               (first_name, last_name, department, email))
                conn.commit()
                refresh_professor_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not add professor: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    tk.Button(popup, text="Add", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

def update_professor():
    selected = professor_tree.focus()
    if not selected:
        messagebox.showwarning("Select Professor", "Please select a professor to update.")
        return
    record = professor_tree.item(selected, "values")
    prof_id = record[0]
    
    popup = tk.Toplevel(root)
    popup.title("Update Professor")
    
    tk.Label(popup, text="First Name:").grid(row=0, column=0, padx=5, pady=5)
    first_name_entry = tk.Entry(popup)
    first_name_entry.insert(0, record[1])
    first_name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Last Name:").grid(row=1, column=0, padx=5, pady=5)
    last_name_entry = tk.Entry(popup)
    last_name_entry.insert(0, record[2])
    last_name_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Department:").grid(row=2, column=0, padx=5, pady=5)
    department_entry = tk.Entry(popup)
    department_entry.insert(0, record[3])
    department_entry.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(popup, text="Email:").grid(row=3, column=0, padx=5, pady=5)
    email_entry = tk.Entry(popup)
    email_entry.insert(0, record[4])
    email_entry.grid(row=3, column=1, padx=5, pady=5)

    def submit():
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        department = department_entry.get()
        email = email_entry.get()
        
        if first_name and last_name and department and email:
            try:
                cursor.execute("UPDATE Professor SET first_name=?, last_name=?, department=?, email=? WHERE professor_id=?",
                               (first_name, last_name, department, email, prof_id))
                conn.commit()
                refresh_professor_tree()
                popup.destroy()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Could not update professor: {e}")
        else:
            messagebox.showwarning("Input Error", "All fields are required.")

    tk.Button(popup, text="Update", command=submit).grid(row=4, column=0, columnspan=2, pady=10)

def delete_professor():
    selected = professor_tree.focus()
    if not selected:
        messagebox.showwarning("Select Professor", "Please select a professor to delete.")
        return
    record = professor_tree.item(selected, "values")
    prof_id = record[0]
    
    # Check if professor is assigned to courses
    cursor.execute("SELECT COUNT(*) FROM CourseAssignment WHERE professor_id = ?", (prof_id,))
    assigned_count = cursor.fetchone()[0]
    
    if assigned_count > 0:
        if messagebox.askyesno("Warning", f"This professor is assigned to {assigned_count} course(s). Deleting will remove all assignments. Continue?"):
            cursor.execute("DELETE FROM CourseAssignment WHERE professor_id=?", (prof_id,))
            cursor.execute("DELETE FROM Professor WHERE professor_id=?", (prof_id,))
            conn.commit()
            refresh_professor_tree()
            refresh_course_tree()  # Refresh course tree to show professor removals
    else:
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this professor?"):
            cursor.execute("DELETE FROM Professor WHERE professor_id=?", (prof_id,))
            conn.commit()
            refresh_professor_tree()

# Buttons for Professor Tab
professor_button_frame = ttk.Frame(professor_frame)
professor_button_frame.pack(pady=5)

ttk.Button(professor_button_frame, text="Add Professor", command=add_professor).pack(side="left", padx=5)
ttk.Button(professor_button_frame, text="Update Professor", command=update_professor).pack(side="left", padx=5)
ttk.Button(professor_button_frame, text="Delete Professor", command=delete_professor).pack(side="left", padx=5)

# -------------
# Setup Database Tables
# -------------

# Create Professor table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Professor (
    professor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
''')

# Create CourseAssignment table for the relationship
cursor.execute('''
CREATE TABLE IF NOT EXISTS CourseAssignment (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id),
    FOREIGN KEY (professor_id) REFERENCES Professor(professor_id),
    UNIQUE(course_id, professor_id)
)
''')
conn.commit()

# Initialize both views
refresh_professor_tree()
refresh_course_tree()
# -------------
# Grade Entry Tab
# -------------
grade_entry_frame = ttk.Frame(notebook)
notebook.add(grade_entry_frame, text="Grade Entry")

# Create treeview to display student grade status
grade_status_tree = ttk.Treeview(grade_entry_frame, columns=("ID", "Student", "Grade Status"), show="headings")
grade_status_tree.heading("ID", text="ID")
grade_status_tree.heading("Student", text="Student")
grade_status_tree.heading("Grade Status", text="Grade Status")
grade_status_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_grade_status_tree():
    # Clear existing data
    for row in grade_status_tree.get_children():
        grade_status_tree.delete(row)
    
    # Get all students
    cursor.execute("SELECT student_id, name FROM Student")
    students = cursor.fetchall()
    
    # Check grade status for each student
    for student_id, name in students:
        grade_file = f"grades_{student_id}.txt"
        status = "Grades Entered" if os.path.exists(grade_file) else "No Grades"
        grade_status_tree.insert("", "end", values=(student_id, name, status))

def enter_grades():
    # Get selected student
    selected = grade_status_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to enter grades for.")
        return
    
    student_data = grade_status_tree.item(selected, "values")
    student_id = student_data[0]
    student_name = student_data[1]
    
    # Check if student has registered for courses
    registration_file = f"registration_{student_id}.txt"
    if not os.path.exists(registration_file):
        messagebox.showinfo("No Registration", f"{student_name} has not registered for any courses.")
        return
    
    # Parse the registration file to get registered courses
    registered_courses = []
    current_semester = None
    with open(registration_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("Semester:"):
                current_semester = line.split(":")[1].strip()
            elif line.startswith("- "):
                # Extract course ID from line like "- 101 - Introduction to Programming"
                course_info = line.strip("- \n")
                try:
                    course_id = int(course_info.split(" - ")[0])
                    registered_courses.append(course_id)
                except (ValueError, IndexError):
                    continue
    
    if not registered_courses:
        messagebox.showinfo("No Courses", f"{student_name} has not registered for any courses.")
        return
    
    # Create grade entry popup
    popup = tk.Toplevel(root)
    popup.title(f"Grade Entry - {student_name}")
    popup.geometry("500x400")
    
    # Create a frame with scrollable area
    main_frame = ttk.Frame(popup)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Canvas with scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Semester info (use the semester from registration)
    semester_frame = ttk.Frame(scrollable_frame)
    semester_frame.pack(fill="x", pady=5)
    ttk.Label(semester_frame, text=f"Semester: {current_semester}").pack(side="left", padx=5)
    semester_var = tk.StringVar(value=current_semester)
    
    # Info label
    ttk.Label(scrollable_frame, text="Enter grades for registered courses:").pack(anchor="w", pady=(10, 0))
    
    # Create grade entry fields for registered courses only
    course_grades = {}
    any_courses_found = False
    
    for course_id in registered_courses:
        # Get course details
        cursor.execute("SELECT course_name FROM Course WHERE course_id = ?", (course_id,))
        result = cursor.fetchone()
        if not result:
            continue
            
        course_name = result[0]
        any_courses_found = True
        
        course_frame = ttk.Frame(scrollable_frame)
        course_frame.pack(fill="x", pady=5)
        
        ttk.Label(course_frame, text=f"{course_id} - {course_name}:").grid(row=0, column=0, padx=5, sticky="w")
        
        grade_var = tk.StringVar()
        grade_entry = ttk.Combobox(course_frame, textvariable=grade_var, values=["AA", "AB", "BB", "BC", "CC", "CD", "DD", "FF"], width=5, state="readonly")
        grade_entry.grid(row=0, column=1, padx=5)
        
        # Store the grade variable with the course_id as the key
        course_grades[course_id] = grade_var
    
    if not any_courses_found:
        ttk.Label(scrollable_frame, text="No registered courses found in the database.").pack(pady=20)
    
    def save_grades():
        semester = semester_var.get()
        if not semester:
            messagebox.showwarning("Error", "Semester information is missing.")
            return
        
        # Check if any grades were entered
        entered_grades = {course_id: grade.get() for course_id, grade in course_grades.items() if grade.get()}
        if not entered_grades:
            messagebox.showwarning("No Grades", "Please enter at least one grade.")
            return
        
        # Convert letter grades to points
        grade_points = {
            "AA": 10.0, "AB": 9.0,
            "BB": 8.0, "BC": 7.0, "CC": 6.0,
            "CD": 5.0, "DD": 4.0,
            "FF": 0.0
        }
        
        # Save grades to file
        grade_file = f"grades_{student_id}.txt"
        with open(grade_file, "w") as f:
            f.write(f"Student ID: {student_id}\n")
            f.write(f"Student Name: {student_name}\n")
            f.write(f"Semester: {semester}\n")
            f.write("Course Grades:\n")
            
            # Calculate GPA
            total_points = 0
            total_courses = 0
            
            for course_id, letter_grade in entered_grades.items():
                # Get course name
                cursor.execute("SELECT course_name FROM Course WHERE course_id = ?", (course_id,))
                course_name = cursor.fetchone()[0]
                
                # Get grade point
                grade_point = grade_points.get(letter_grade, 0)
                
                # Save to file
                f.write(f"- {course_id} - {course_name}: {letter_grade} ({grade_point})\n")
                
                # Add to database
                try:
                    cursor.execute("""
                        INSERT INTO Grade (student_id, course_id, semester, grade_point) 
                        VALUES (?, ?, ?, ?)
                    """, (student_id, course_id, int(semester), grade_point))
                    conn.commit()
                except Exception as e:
                    # If grade already exists, update it
                    cursor.execute("""
                        UPDATE Grade SET grade_point = ? 
                        WHERE student_id = ? AND course_id = ? AND semester = ?
                    """, (grade_point, student_id, course_id, int(semester)))
                    conn.commit()
                
                total_points += grade_point
                total_courses += 1
            
            # Calculate and save GPA
            if total_courses > 0:
                gpa = total_points / total_courses
                f.write(f"\nSemester GPA: {gpa:.2f}\n")
            
            f.write(f"Date Entered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        messagebox.showinfo("Grades Saved", f"Grades for {student_name} have been saved.")
        refresh_grade_status_tree()
        popup.destroy()
    
    # Add buttons
    button_frame = ttk.Frame(popup)
    button_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Button(button_frame, text="Save Grades", command=save_grades).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)

def view_grades():
    # Get selected student
    selected = grade_status_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to view grades.")
        return
    
    student_data = grade_status_tree.item(selected, "values")
    student_id = student_data[0]
    student_name = student_data[1]
    
    grade_file = f"grades_{student_id}.txt"
    if not os.path.exists(grade_file):
        messagebox.showinfo("No Grades", f"No grades have been entered for {student_name}.")
        return
    
    # Display grade details
    popup = tk.Toplevel(root)
    popup.title(f"Grade Details - {student_name}")
    popup.geometry("400x300")
    
    # Create text widget with scrollbar
    text_frame = ttk.Frame(popup)
    text_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    
    text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
    
    with open(grade_file, "r") as f:
        content = f.read()
    
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")  # Make read-only
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)
    
    ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

def delete_grades():
    # Get selected student
    selected = grade_status_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to delete grades.")
        return
    
    student_data = grade_status_tree.item(selected, "values")
    student_id = student_data[0]
    student_name = student_data[1]
    
    grade_file = f"grades_{student_id}.txt"
    if not os.path.exists(grade_file):
        messagebox.showinfo("No Grades", f"No grades have been entered for {student_name}.")
        return
    
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the grades for {student_name}?"):
        # Delete from file
        os.remove(grade_file)
        
        # Delete from database
        try:
            cursor.execute("DELETE FROM Grade WHERE student_id = ?", (student_id,))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete grades from database: {e}")
            
        refresh_grade_status_tree()
        messagebox.showinfo("Grades Deleted", f"Grades for {student_name} have been deleted.")

# Create buttons for grade entry tab
button_frame = ttk.Frame(grade_entry_frame)
button_frame.pack(fill="x", padx=10, pady=5)

ttk.Button(button_frame, text="Enter Grades", command=enter_grades).pack(side="left", padx=5)
ttk.Button(button_frame, text="View Grades", command=view_grades).pack(side="left", padx=5)
ttk.Button(button_frame, text="Delete Grades", command=delete_grades).pack(side="left", padx=5)
ttk.Button(button_frame, text="Refresh", command=refresh_grade_status_tree).pack(side="left", padx=5)

# Initialize the grade status tree
refresh_grade_status_tree()

registration_frame = ttk.Frame(notebook)
notebook.add(registration_frame, text="Course Registration")

# Create treeview to display registration status
registration_tree = ttk.Treeview(registration_frame, columns=("ID", "Student", "Registration Status"), show="headings")
registration_tree.heading("ID", text="ID")
registration_tree.heading("Student", text="Student")
registration_tree.heading("Registration Status", text="Registration Status")
registration_tree.pack(fill="both", expand=True, padx=10, pady=10)

def refresh_registration_tree():
    # Clear existing data
    for row in registration_tree.get_children():
        registration_tree.delete(row)
    
    # Get all students
    cursor.execute("SELECT student_id, name FROM Student")
    students = cursor.fetchall()
    
    # Check registration status for each student
    for student_id, name in students:
        registration_file = f"registration_{student_id}.txt"
        status = "Completed" if os.path.exists(registration_file) else "Not Registered"
        registration_tree.insert("", "end", values=(student_id, name, status))

def register_courses():
    # Get selected student
    selected = registration_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to register courses for.")
        return
    
    student_data = registration_tree.item(selected, "values")
    student_id = student_data[0]
    student_name = student_data[1]
    
    # Create registration popup
    popup = tk.Toplevel(root)
    popup.title(f"Course Registration - {student_name}")
    popup.geometry("500x400")
    
    # Get all available courses
    cursor.execute("SELECT course_id, course_name FROM Course")
    courses = cursor.fetchall()
    
    # Create a frame for the course selection with scrollbar
    course_frame = ttk.Frame(popup)
    course_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(course_frame)
    scrollbar.pack(side="right", fill="y")
    
    # Create listbox with courses
    course_listbox = tk.Listbox(course_frame, selectmode="multiple", yscrollcommand=scrollbar.set)
    for course_id, course_name in courses:
        course_listbox.insert(tk.END, f"{course_id} - {course_name}")
    course_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=course_listbox.yview)
    
    # Add semester selection
    semester_frame = ttk.Frame(popup)
    semester_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(semester_frame, text="Semester:").pack(side="left", padx=5)
    semester_var = tk.StringVar()
    semester_combo = ttk.Combobox(semester_frame, textvariable=semester_var, values=["1", "2", "3", "4", "5", "6", "7", "8"], state="readonly")
    semester_combo.pack(side="left", padx=5)
    semester_combo.current(0)
    
    def save_registration():
        selected_indices = course_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Courses", "Please select at least one course.")
            return
        
        semester = semester_var.get()
        if not semester:
            messagebox.showwarning("No Semester", "Please select a semester.")
            return
        
        # Get selected courses
        selected_courses = [course_listbox.get(i) for i in selected_indices]
        
        # Save registration data to file
        registration_file = f"registration_{student_id}.txt"
        with open(registration_file, "w") as f:
            f.write(f"Student ID: {student_id}\n")
            f.write(f"Student Name: {student_name}\n")
            f.write(f"Semester: {semester}\n")
            f.write("Registered Courses:\n")
            for course in selected_courses:
                f.write(f"- {course}\n")
            f.write(f"Registration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        messagebox.showinfo("Registration Complete", f"Course registration completed for {student_name}.")
        refresh_registration_tree()
        popup.destroy()
    
    # Add buttons
    button_frame = ttk.Frame(popup)
    button_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Button(button_frame, text="Register", command=save_registration).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=5)

def view_registration():
    # Get selected student
    selected = registration_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to view registration.")
        return
    
    student_data = registration_tree.item(selected, "values")
    student_id = student_data[0]
    student_name = student_data[1]
    
    registration_file = f"registration_{student_id}.txt"
    if not os.path.exists(registration_file):
        messagebox.showinfo("No Registration", f"{student_name} has not registered for any courses.")
        return
    
    # Display registration details
    popup = tk.Toplevel(root)
    popup.title(f"Registration Details - {student_name}")
    popup.geometry("400x300")
    
    # Create text widget with scrollbar
    text_frame = ttk.Frame(popup)
    text_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    
    text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
    
    with open(registration_file, "r") as f:
        content = f.read()
    
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")  # Make read-only
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)
    
    ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

def delete_registration():
    # Get selected student
    selected = registration_tree.focus()
    if not selected:
        messagebox.showwarning("Select Student", "Please select a student to delete registration.")
        return
    
    student_data = registration_tree.item(selected, "values")
    student_id = student_data[0]
    student_name = student_data[1]
    
    registration_file = f"registration_{student_id}.txt"
    if not os.path.exists(registration_file):
        messagebox.showinfo("No Registration", f"{student_name} has not registered for any courses.")
        return
    
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the registration for {student_name}?"):
        os.remove(registration_file)
        refresh_registration_tree()
        messagebox.showinfo("Registration Deleted", f"Registration for {student_name} has been deleted.")

# Create buttons
button_frame = ttk.Frame(registration_frame)
button_frame.pack(fill="x", padx=10, pady=5)

ttk.Button(button_frame, text="Register Courses", command=register_courses).pack(side="left", padx=5)
ttk.Button(button_frame, text="View Registration", command=view_registration).pack(side="left", padx=5)
ttk.Button(button_frame, text="Delete Registration", command=delete_registration).pack(side="left", padx=5)
ttk.Button(button_frame, text="Refresh", command=refresh_registration_tree).pack(side="left", padx=5)



# Initialize the registration tree
refresh_registration_tree()



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