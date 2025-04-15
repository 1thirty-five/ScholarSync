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

# Define color palette
# Color scheme based on the blue-grey-white reference
BACKGROUND_COLOR = "#f0f2f5"
PRIMARY_COLOR = "#3b5998"  # Blue color for headings and primary buttons
SECONDARY_COLOR = "#e0e0e0"  # Light grey for secondary buttons
TEXT_COLOR = "#333333"
ACCENT_COLOR = "#f8f9fa"  # Very light grey for section backgrounds
WHITE = "#ffffff"



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
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Create a notebook (tabbed interface)
style = ttk.Style()
style.configure("TNotebook", background=BACKGROUND_COLOR)
style.configure("TNotebook.Tab", background=SECONDARY_COLOR, padding=[10, 5])
style.configure("TFrame", background=BACKGROUND_COLOR)
style.configure("TLabelframe", background=BACKGROUND_COLOR)
style.configure("TLabelframe.Label", background=BACKGROUND_COLOR, foreground=PRIMARY_COLOR, font=("Arial", 11, "bold"))
style.configure("TButton", background=PRIMARY_COLOR, foreground="white", font=("Arial", 10, "bold"))
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

# Professor Tab (keeping original structure)
professor_frame = ttk.Frame(notebook)
notebook.add(professor_frame, text="Professors")

# Set up the professor treeview with improved styling
professor_tree = ttk.Treeview(professor_frame, columns=("ID", "First Name", "Last Name", "Department", "Email"), 
                             show="headings")

# Configure column widths
professor_tree.column("ID", width=50, anchor="center")
professor_tree.column("First Name", width=120)
professor_tree.column("Last Name", width=120)
professor_tree.column("Department", width=150)
professor_tree.column("Email", width=200)

# Configure column headings
professor_tree.heading("ID", text="ID")
professor_tree.heading("First Name", text="First Name")
professor_tree.heading("Last Name", text="Last Name")
professor_tree.heading("Department", text="Department")
professor_tree.heading("Email", text="Email")

# Add scrollbar
y_scrollbar = ttk.Scrollbar(professor_frame, orient="vertical", command=professor_tree.yview)
professor_tree.configure(yscrollcommand=y_scrollbar.set)

# Position treeview and scrollbar
professor_tree.pack(fill="both", expand=True, padx=10, pady=10)
y_scrollbar.place(relx=1.0, rely=0.0, relheight=0.9, anchor='ne')


# Keep the original refresh function
def refresh_professor_tree():
    for row in professor_tree.get_children():
        professor_tree.delete(row)
    cursor.execute("SELECT * FROM Professor")
    for row in cursor.fetchall():
        professor_tree.insert("", "end", values=row)

# Modified popup styling for add_professor function
def add_professor():
    popup = tk.Toplevel(root)
    popup.title("Add Professor")
    popup.configure(bg=WHITE)
    popup.geometry("350x250")
    
    # Add some padding around the form
    form_frame = tk.Frame(popup, bg=WHITE, padx=15, pady=15)
    form_frame.pack(fill="both", expand=True)

    tk.Label(form_frame, text="First Name:", bg=WHITE, fg=TEXT_COLOR).grid(row=0, column=0, padx=5, pady=8, sticky="w")
    first_name_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    first_name_entry.grid(row=0, column=1, padx=5, pady=8)
    
    tk.Label(form_frame, text="Last Name:", bg=WHITE, fg=TEXT_COLOR).grid(row=1, column=0, padx=5, pady=8, sticky="w")
    last_name_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    last_name_entry.grid(row=1, column=1, padx=5, pady=8)
    
    tk.Label(form_frame, text="Department:", bg=WHITE, fg=TEXT_COLOR).grid(row=2, column=0, padx=5, pady=8, sticky="w")
    department_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    department_entry.grid(row=2, column=1, padx=5, pady=8)
    
    tk.Label(form_frame, text="Email:", bg=WHITE, fg=TEXT_COLOR).grid(row=3, column=0, padx=5, pady=8, sticky="w")
    email_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    email_entry.grid(row=3, column=1, padx=5, pady=8)

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

    # Button frame
    button_frame = tk.Frame(form_frame, bg=WHITE)
    button_frame.grid(row=4, column=0, columnspan=2, pady=15)
    
    # Add buttons with custom colors
    add_btn = tk.Button(button_frame, text="Add", bg=PRIMARY_COLOR, fg=WHITE, command=submit, padx=10)
    add_btn.pack(side="right", padx=5)
    
    cancel_btn = tk.Button(button_frame, text="Cancel", bg=SECONDARY_COLOR, fg=TEXT_COLOR, command=popup.destroy, padx=10)
    cancel_btn.pack(side="right", padx=5)


def delete_professor():
    # Get the currently selected item in the treeview
    selected = professor_tree.focus()
    
    # Check if an item is selected
    if not selected:
        messagebox.showwarning("Select Professor", "Please select a professor to delete.")
        return
    
    # Get the values (data) from the selected item
    record = professor_tree.item(selected, "values")
    prof_id = record[0]  # The first column is the professor ID
    
    # Check if professor is assigned to any courses
    cursor.execute("SELECT COUNT(*) FROM CourseAssignment WHERE professor_id = ?", (prof_id,))
    assigned_count = cursor.fetchone()[0]
    
    if assigned_count > 0:
        # Professor has course assignments - ask for confirmation
        if messagebox.askyesno("Warning", 
                            f"This professor is assigned to {assigned_count} course(s). " 
                            f"Deleting will remove all assignments. Continue?",
                            icon='warning'):
            try:
                # Delete the course assignments first (foreign key constraint)
                cursor.execute("DELETE FROM CourseAssignment WHERE professor_id=?", (prof_id,))
                
                # Then delete the professor
                cursor.execute("DELETE FROM Professor WHERE professor_id=?", (prof_id,))
                
                # Commit the changes to the database
                conn.commit()
                
                # Refresh the treeview to show the updated data
                refresh_professor_tree()
                
                # Also refresh the course tree if it exists (to show professor removals)
                if 'refresh_course_tree' in globals():
                    refresh_course_tree()
                    
                messagebox.showinfo("Success", "Professor and associated course assignments deleted successfully.")
            except sqlite3.Error as e:
                # Show error message if delete operation fails
                messagebox.showerror("Database Error", f"Failed to delete professor: {e}")
                conn.rollback()  # Roll back the transaction
    else:
        # Professor has no course assignments - simple confirmation
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete professor {record[1]} {record[2]}?"):
            try:
                # Delete the professor
                cursor.execute("DELETE FROM Professor WHERE professor_id=?", (prof_id,))
                
                # Commit the changes
                conn.commit()
                
                # Refresh the treeview
                refresh_professor_tree()
                
                messagebox.showinfo("Success", "Professor deleted successfully.")
            except sqlite3.Error as e:
                # Show error message if delete operation fails
                messagebox.showerror("Database Error", f"Failed to delete professor: {e}")
                conn.rollback()  # Roll back the transaction
                
# Modified popup styling for update_professor function (similar changes)
def update_professor():
    selected = professor_tree.focus()
    if not selected:
        messagebox.showwarning("Select Professor", "Please select a professor to update.")
        return
    record = professor_tree.item(selected, "values")
    prof_id = record[0]
    
    popup = tk.Toplevel(root)
    popup.title("Update Professor")
    popup.configure(bg=WHITE)
    popup.geometry("350x250")
    
    # Add some padding around the form
    form_frame = tk.Frame(popup, bg=WHITE, padx=15, pady=15)
    form_frame.pack(fill="both", expand=True)
    
    tk.Label(form_frame, text="First Name:", bg=WHITE, fg=TEXT_COLOR).grid(row=0, column=0, padx=5, pady=8, sticky="w")
    first_name_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    first_name_entry.insert(0, record[1])
    first_name_entry.grid(row=0, column=1, padx=5, pady=8)
    
    tk.Label(form_frame, text="Last Name:", bg=WHITE, fg=TEXT_COLOR).grid(row=1, column=0, padx=5, pady=8, sticky="w")
    last_name_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    last_name_entry.insert(0, record[2])
    last_name_entry.grid(row=1, column=1, padx=5, pady=8)
    
    tk.Label(form_frame, text="Department:", bg=WHITE, fg=TEXT_COLOR).grid(row=2, column=0, padx=5, pady=8, sticky="w")
    department_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    department_entry.insert(0, record[3])
    department_entry.grid(row=2, column=1, padx=5, pady=8)
    
    tk.Label(form_frame, text="Email:", bg=WHITE, fg=TEXT_COLOR).grid(row=3, column=0, padx=5, pady=8, sticky="w")
    email_entry = tk.Entry(form_frame, bg=WHITE, fg=TEXT_COLOR)
    email_entry.insert(0, record[4])
    email_entry.grid(row=3, column=1, padx=5, pady=8)

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
        # Buttons for Professor Tab with custom colors
        professor_button_frame = ttk.Frame(professor_frame)
        professor_button_frame.pack(pady=5, padx=10, fill="x")


    # Button frame
    button_frame = tk.Frame(form_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=15)
    
    # Add buttons with custom colors
    update_btn = tk.Button(button_frame, text="Update", bg=PRIMARY_COLOR, fg=WHITE, command=submit, padx=10)
    update_btn.pack(side="right", padx=5)
    
    cancel_btn = tk.Button(button_frame, text="Cancel", bg=SECONDARY_COLOR, fg=TEXT_COLOR, command=popup.destroy, padx=10)
    cancel_btn.pack(side="right", padx=5)


# but messagebox appearance will be affected by system settings

# Buttons for Professor Tab with custom colors
professor_button_frame = ttk.Frame(professor_frame)
professor_button_frame.pack(pady=5, padx=10, fill="x")

# Use the custom button styles
add_button = tk.Button(professor_button_frame, text="Add Professor", command=add_professor, bg=PRIMARY_COLOR, fg=WHITE, font=("Arial", 10), padx=10, pady=10)
add_button.pack(side="left", padx=5)

update_button = tk.Button(professor_button_frame, text="Update Professor", command=update_professor, bg=PRIMARY_COLOR, fg=WHITE, font=("Arial", 10), padx=10, pady=10)
update_button.pack(side="left", padx=5)

delete_button = tk.Button(professor_button_frame, text="Delete Professor", command=delete_professor, bg=PRIMARY_COLOR, fg=WHITE, font=("Arial", 10), padx=10, pady=10)
delete_button.pack(side="left", padx=5)

# Initialize the view
refresh_professor_tree() 
    
# -------------
# Grade Entry Tab
# -------------
# Create the grade entry frame
grade_entry_frame = ttk.Frame(notebook)
notebook.add(grade_entry_frame, text="Grade Entry")

# Add a blue header
header_frame = ttk.Frame(grade_entry_frame, style="Blue.TFrame")
header_frame.pack(fill="x")
header_label = ttk.Label(header_frame, text="Grade Entry", style="Blue.TLabel")
header_label.pack(pady=10)

# Create treeview to display student grade status
tree_frame = ttk.Frame(grade_entry_frame)
tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Add a search bar
search_frame = ttk.Frame(grade_entry_frame)
search_frame.pack(fill="x", padx=10, pady=(5, 0))

search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, width=25)
search_entry.pack(side="left", padx=5)
search_label = ttk.Label(search_frame, text="Search:")
search_label.pack(side="left", padx=(0, 5))

# Create scrollbar for treeview
scrollbar = ttk.Scrollbar(tree_frame)
scrollbar.pack(side="right", fill="y")

grade_status_tree = ttk.Treeview(tree_frame, columns=("ID", "Student", "Grade Status"), 
                                show="headings", yscrollcommand=scrollbar.set)
grade_status_tree.heading("ID", text="ID")
grade_status_tree.heading("Student", text="Student")
grade_status_tree.heading("Grade Status", text="Grade Status")

# Set column widths
grade_status_tree.column("ID", width=80)
grade_status_tree.column("Student", width=200)
grade_status_tree.column("Grade Status", width=120)

grade_status_tree.pack(fill="both", expand=True, padx=10, pady=10)
scrollbar.config(command=grade_status_tree.yview)

# Apply custom tags for status coloring
grade_status_tree.tag_configure("grades_entered", background="#e6ffe6")  # Light green
grade_status_tree.tag_configure("no_grades", background="#fff9e6")       # Light yellow

# Add this code to your database initialization section
# (where you created the Professor and CourseAssignment tables)

# Create Student table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Student (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    program TEXT NOT NULL
)
''')

# Create Grade table for storing student grades if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Grade (
    grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id),
    UNIQUE(student_id, course_id)
)
''')
conn.commit()

# Then modify your refresh_grade_status_tree function to handle the case 
# where the table exists but might be empty
def refresh_grade_status_tree():
    # Clear existing items
    for row in grade_status_tree.get_children():
        grade_status_tree.delete(row)
    
    try:
        # Check if the Student table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Student'")
        if cursor.fetchone() is None:
            messagebox.showwarning("Missing Table", "Student table doesn't exist. Creating it now.")
            # Create the table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Student (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                program TEXT NOT NULL
            )
            ''')
            conn.commit()
            return  # Return early since the table will be empty
            
        # Fetch students
        cursor.execute("SELECT student_id, name FROM Student")
        students = cursor.fetchall()
        
        if not students:
            # If no data, insert a sample student for testing
            sample_data = [
                ("John Doe", "john.doe@university.edu", "Computer Science"),
                ("Jane Smith", "jane.smith@university.edu", "Mathematics")
            ]
            cursor.executemany("INSERT INTO Student (name, email, program) VALUES (?, ?, ?)", sample_data)
            conn.commit()
            
            # Now fetch again
            cursor.execute("SELECT student_id, name FROM Student")
            students = cursor.fetchall()
        
        # Display in treeview
        for student in students:
            grade_status_tree.insert("", "end", values=student)
            
    except sqlite3.OperationalError as e:
        messagebox.showerror("Database Error", f"Error accessing student data: {e}")

# Search function
def search_students():
    refresh_grade_status_tree()

# Add search button
search_button = tk.Button(search_frame, text="Search", bg="#3b5998", fg="white",
                        font=("Arial", 10), padx=10, pady=2, bd=0,
                        command=search_students)
search_button.pack(side="left", padx=5)

# Clear search button
clear_button = tk.Button(search_frame, text="Clear", bg="#d3d3d3", fg="black",
                       font=("Arial", 10), padx=10, pady=2, bd=0,
                       command=lambda: [search_var.set(""), refresh_grade_status_tree()])
clear_button.pack(side="left", padx=5)

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
    popup.configure(bg="#f0f0f0")
    popup.grab_set()  # Make window modal
    
    # Add blue header
    popup_header = tk.Frame(popup, bg="#3b5998", padx=10, pady=10)
    popup_header.pack(fill="x")
    popup_title = tk.Label(popup_header, text=f"Grade Entry - {student_name}", 
                         font=("Arial", 12, "bold"), bg="#3b5998", fg="white")
    popup_title.pack()
    
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
    ttk.Label(semester_frame, text=f"Semester:").pack(side="left", padx=5)
    semester_var = tk.StringVar(value=current_semester)
    
    semester_combo = ttk.Combobox(semester_frame, textvariable=semester_var, 
                                width=15, values=["1", "2", "3","4", "5", "6","7", "8"], 
                                state="readonly")
    semester_combo.pack(side="left", padx=5)
    
    # Info label
    ttk.Label(scrollable_frame, text="Enter grades for registered courses:", 
             font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    
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
        grade_entry = ttk.Combobox(course_frame, textvariable=grade_var, 
                                 values=["AA", "AB", "BB", "BC", "CC", "CD", "DD", "FF"], 
                                 width=5, state="readonly")
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
                # If the semester is just a number like "1", "2", etc.
                    if semester.isdigit():
                        semester_num = int(semester)
                    
                    else:
                    # Extract digits from the string
                        digits = ''.join(filter(str.isdigit, semester))
                        semester_num = int(digits) if digits else 1  # Default to 1 if no digits found
            
                    cursor.execute("""
                        INSERT INTO Grade (student_id, course_id, semester, grade_point) 
                        VALUES (?, ?, ?, ?)
                    """, (student_id, course_id, semester_num, grade_point))
                    conn.commit()
                except ValueError:
                # If conversion fails, use a default value
                    cursor.execute("""
                        INSERT INTO Grade (student_id, course_id, semester, grade_point) 
                        ALUES (?, ?, ?, ?)
                    """, (student_id, course_id, 1, grade_point))  # Default to semester 1    
                except Exception as e:
                    # If grade already exists, update it
                    cursor.execute("""
                        UPDATE Grade SET grade_point = ? 
                        WHERE student_id = ? AND course_id = ? AND semester = ?
                    """, (grade_point, student_id, course_id, int(semester.split()[1])))
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
    
    save_button = tk.Button(button_frame, text="Save Grades", bg="#3b5998", fg="white",
                          font=("Arial", 10), padx=10, pady=2, bd=0, command=save_grades)
    save_button.pack(side="right", padx=5)
    
    cancel_button = tk.Button(button_frame, text="Cancel", bg="#d3d3d3", fg="black",
                            font=("Arial", 10), padx=10, pady=2, bd=0, command=popup.destroy)
    cancel_button.pack(side="right", padx=5)

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
    popup.configure(bg="#f0f0f0")
    popup.grab_set()  # Make window modal
    
    # Add blue header
    popup_header = tk.Frame(popup, bg="#3b5998", padx=10, pady=10)
    popup_header.pack(fill="x")
    popup_title = tk.Label(popup_header, text=f"Grade Details - {student_name}", 
                         font=("Arial", 12, "bold"), bg="#3b5998", fg="white")
    popup_title.pack()
    
    # Create text widget with scrollbar
    text_frame = ttk.Frame(popup)
    text_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")
    
    text_widget = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, bg="white", fg="black")
    
    with open(grade_file, "r") as f:
        content = f.read()
    
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")  # Make read-only
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)
    
    close_button = tk.Button(popup, text="Close", bg="#3b5998", fg="white",
                          font=("Arial", 10), padx=10, pady=2, bd=0, command=popup.destroy)
    close_button.pack(pady=10)

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

# Using custom tk Buttons for blue styling instead of ttk
enter_btn = tk.Button(button_frame, text="Enter Grades", command=enter_grades,
                    bg="#3b5998", fg="white", font=("Arial", 10), padx=10, pady=2, bd=0)
enter_btn.pack(side="left", padx=5)

view_btn = tk.Button(button_frame, text="View Grades", command=view_grades,
                   bg="#3b5998", fg="white", font=("Arial", 10), padx=10, pady=2, bd=0)
view_btn.pack(side="left", padx=5)

delete_btn = tk.Button(button_frame, text="Delete Grades", command=delete_grades,
                     bg="#3b5998", fg="white", font=("Arial", 10), padx=10, pady=2, bd=0)
delete_btn.pack(side="left", padx=5)

refresh_btn = tk.Button(button_frame, text="Refresh", command=refresh_grade_status_tree,
                      bg="#d3d3d3", fg="black", font=("Arial", 10), padx=10, pady=2, bd=0)
refresh_btn.pack(side="left", padx=5)

# Initialize the grade status tree
refresh_grade_status_tree()


# -------------
# Course Registration Tab
# -------------

registration_frame = ttk.Frame(notebook)
notebook.add(registration_frame, text="Course Registration")

# Top part: Header
header_frame = ttk.Frame(registration_frame)
header_frame.pack(fill="x", padx=10, pady=10)

header_label = tk.Label(header_frame, text="Course Registration", 
                        font=("Arial", 18, "bold"), 
                        fg=PRIMARY_COLOR,
                        bg=BACKGROUND_COLOR)
header_label.pack(pady=10)

# Middle part: Registration Status Display
status_frame = ttk.LabelFrame(registration_frame, text="Registration Status")
status_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Style for the treeview (already defined in the previous code)

# Create treeview to display registration status
registration_tree = ttk.Treeview(status_frame, columns=("ID", "Student", "Registration Status"), show="headings", height=10)
registration_tree.heading("ID", text="ID")
registration_tree.heading("Student", text="Student")
registration_tree.heading("Registration Status", text="Registration Status")
registration_tree.column("ID", width=100)
registration_tree.column("Student", width=250)
registration_tree.column("Registration Status", width=150)
registration_tree.pack(fill="both", expand=True, padx=10, pady=10)

# Add scrollbar to treeview
reg_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=registration_tree.yview)
registration_tree.configure(yscrollcommand=reg_scrollbar.set)
reg_scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')

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
        
        # Add color indicator based on status
        tag = "registered" if status == "Completed" else "not_registered"
        item_id = registration_tree.insert("", "end", values=(student_id, name, status), tags=(tag,))
    
    # Configure tag colors
    registration_tree.tag_configure("registered", background="#e3f2fd")  # Light blue background for registered
    registration_tree.tag_configure("not_registered", background="#ffebee")  # Light red background for not registered

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
    popup.geometry("550x500")
    popup.configure(bg=BACKGROUND_COLOR)
    
    # Header in popup
    popup_header = tk.Label(popup, text=f"Register Courses for {student_name}", 
                            font=("Arial", 14, "bold"), 
                            fg=PRIMARY_COLOR,
                            bg=BACKGROUND_COLOR)
    popup_header.pack(pady=15)
    
    # Get all available courses
    cursor.execute("SELECT course_id, course_name, credits FROM Course")
    courses = cursor.fetchall()
    
    # Create a frame for the course selection
    course_frame = ttk.LabelFrame(popup, text="Available Courses")
    course_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    # Create inner frame to hold listbox and scrollbar
    course_inner_frame = ttk.Frame(course_frame)
    course_inner_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(course_inner_frame)
    scrollbar.pack(side="right", fill="y")
    
    # Create listbox with courses
    course_listbox = tk.Listbox(course_inner_frame, 
                               selectmode="multiple", 
                               yscrollcommand=scrollbar.set,
                               font=("Arial", 11),
                               bg="white",
                               highlightthickness=1,
                               highlightbackground="#ccc",
                               selectbackground=PRIMARY_COLOR,
                               selectforeground="white",
                               height=12)
    
    for course_id, course_name, credits in courses:
        course_listbox.insert(tk.END, f"{course_id} - {course_name} ({credits} credits)")
    
    course_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=course_listbox.yview)
    
    # Add semester selection
    semester_frame = ttk.LabelFrame(popup, text="Semester Information")
    semester_frame.pack(fill="x", padx=15, pady=10)
    
    semester_inner_frame = ttk.Frame(semester_frame)
    semester_inner_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(semester_inner_frame, text="Select Semester:", font=("Arial", 11)).pack(side="left", padx=5)
    semester_var = tk.StringVar()
    semester_combo = ttk.Combobox(semester_inner_frame, 
                                 textvariable=semester_var, 
                                 values=["1", "2", "3", "4", "5", "6", "7", "8"], 
                                 state="readonly",
                                 width=10)
    semester_combo.pack(side="left", padx=5)
    semester_combo.current(0)
    
    # Add note about selection
    note_label = tk.Label(popup, 
                        text="Note: Hold Ctrl key to select multiple courses", 
                        font=("Arial", 10, "italic"),
                        fg="#555",
                        bg=BACKGROUND_COLOR)
    note_label.pack(pady=5)
    
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
    button_frame.pack(fill="x", padx=15, pady=15)
    
    # Register button (blue)
    register_button = tk.Button(button_frame, 
                            text="Register", 
                            command=save_registration,
                            bg=PRIMARY_COLOR,
                            fg="white",
                            font=("Arial", 11, "bold"),
                            padx=15,
                            pady=5,
                            borderwidth=0)
    register_button.pack(side="right", padx=5)
    
    # Cancel button (grey)
    cancel_button = tk.Button(button_frame, 
                            text="Cancel", 
                            command=popup.destroy,
                            bg=SECONDARY_COLOR,
                            fg=TEXT_COLOR,
                            font=("Arial", 11),
                            padx=15,
                            pady=5,
                            borderwidth=0)
    cancel_button.pack(side="right", padx=5)

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
    popup.geometry("500x400")
    popup.configure(bg=BACKGROUND_COLOR)
    
    # Header
    popup_header = tk.Label(popup, text=f"Registration Details for {student_name}", 
                            font=("Arial", 14, "bold"), 
                            fg=PRIMARY_COLOR,
                            bg=BACKGROUND_COLOR)
    popup_header.pack(pady=15)
    
    # Create text widget with scrollbar in a frame
    text_frame = ttk.LabelFrame(popup, text="Course Registration Information")
    text_frame.pack(fill="both", expand=True, padx=15, pady=10)
    
    text_inner_frame = ttk.Frame(text_frame)
    text_inner_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(text_inner_frame)
    scrollbar.pack(side="right", fill="y")
    
    text_widget = tk.Text(text_inner_frame, 
                        wrap="word", 
                        yscrollcommand=scrollbar.set,
                        font=("Arial", 11),
                        bg="white",
                        highlightthickness=1,
                        highlightbackground="#ccc",
                        padx=10,
                        pady=10)
    
    with open(registration_file, "r") as f:
        content = f.read()
    
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")  # Make read-only
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)
    
    # Close button
    close_button = tk.Button(popup, 
                            text="Close", 
                            command=popup.destroy,
                            bg=SECONDARY_COLOR,
                            fg=TEXT_COLOR,
                            font=("Arial", 11),
                            padx=20,
                            pady=5,
                            borderwidth=0)
    close_button.pack(pady=15)

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

# Create action buttons in a dedicated frame
action_frame = ttk.LabelFrame(registration_frame, text="Actions")
action_frame.pack(fill="x", padx=10, pady=10)

button_frame = ttk.Frame(action_frame)
button_frame.pack(fill="x", padx=10, pady=10)

# Register Courses button (blue)
register_button = tk.Button(button_frame, 
                            text="Register Courses", 
                            command=register_courses,
                            bg=PRIMARY_COLOR,
                            fg="white",
                            font=("Arial", 11, "bold"),
                            padx=10,
                            pady=5,
                            borderwidth=0)
register_button.pack(side="left", padx=5)

# View Registration button (blue)
view_button = tk.Button(button_frame, 
                        text="View Registration", 
                        command=view_registration,
                        bg=PRIMARY_COLOR,
                        fg="white",
                        font=("Arial", 11, "bold"),
                        padx=10,
                        pady=5,
                        borderwidth=0)
view_button.pack(side="left", padx=5)

# Delete Registration button (with red accent for caution)
delete_button = tk.Button(button_frame, 
                        text="Delete Registration", 
                        command=delete_registration,
                        bg="#f44336",  # Red for danger
                        fg="white",
                        font=("Arial", 11, "bold"),
                        padx=10,
                        pady=5,
                        borderwidth=0)
delete_button.pack(side="left", padx=5)

# Refresh button (grey)
refresh_button = tk.Button(button_frame, 
                        text="Refresh", 
                        command=refresh_registration_tree,
                        bg=SECONDARY_COLOR,
                        fg=TEXT_COLOR,
                        font=("Arial", 11),
                        padx=10,
                        pady=5,
                        borderwidth=0)
refresh_button.pack(side="left", padx=5)

# Help note
help_frame = ttk.Frame(registration_frame)
help_frame.pack(fill="x", padx=10, pady=5)

help_text = "Select a student from the list and use the buttons above to manage course registrations."
help_label = tk.Label(help_frame, 
                    text=help_text, 
                    font=("Arial", 10, "italic"),
                    fg="#555",
                    bg=BACKGROUND_COLOR)
help_label.pack(side="left", padx=10)

# Initialize the registration tree
refresh_registration_tree()

# -------------
# CGPA Calculator Tab
# -------------

calculator_frame = ttk.Frame(notebook)
notebook.add(calculator_frame, text="CGPA Calculator")

# Top part: Header
header_frame = ttk.Frame(calculator_frame)
header_frame.pack(fill="x", padx=10, pady=10)

header_label = tk.Label(header_frame, text="CGPA Calculator", 
                        font=("Arial", 18, "bold"), 
                        fg=PRIMARY_COLOR,
                        bg=BACKGROUND_COLOR)
header_label.pack(pady=10)

# Top part: Student Selection
calc_top_frame = ttk.Frame(calculator_frame)
calc_top_frame.pack(fill="x", padx=10, pady=10)

# Create a styled frame for student selection
selection_frame = ttk.LabelFrame(calc_top_frame, text="Student Selection")
selection_frame.pack(fill="x", padx=5, pady=5)

selection_inner_frame = ttk.Frame(selection_frame)
selection_inner_frame.pack(fill="x", padx=10, pady=10)

tk.Label(selection_inner_frame, text="Select Student:", 
        bg=BACKGROUND_COLOR, 
        fg=TEXT_COLOR,
        font=("Arial", 11)).pack(side="left", padx=5)

student_var = tk.StringVar()

# Function to fetch and populate student list
def populate_student_list():
    cursor.execute("SELECT student_id, name FROM Student")
    students = cursor.fetchall()
    student_choices = {f"{sid} - {name}": sid for sid, name in students}
    student_menu['values'] = list(student_choices.keys())
    return student_choices

# Create the dropdown but we'll populate it later
student_menu = ttk.Combobox(selection_inner_frame, textvariable=student_var, 
                        width=30, state="readonly")
student_menu.pack(side="left", padx=5, fill="x", expand=True)

# Initial population of the dropdown
student_choices = populate_student_list()

# Middle part: Results Display
results_frame = ttk.LabelFrame(calculator_frame, text="GPA Results")
results_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Style for the treeview
style.configure("Treeview", 
                background="white", 
                foreground=TEXT_COLOR, 
                rowheight=25,
                fieldbackground="white")
style.map("Treeview", background=[("selected", PRIMARY_COLOR)])
style.configure("Treeview.Heading", 
                background=ACCENT_COLOR, 
                foreground=TEXT_COLOR, 
                font=("Arial", 10, "bold"))

# Create a treeview for semester-wise SGPA
sgpa_tree = ttk.Treeview(results_frame, columns=("Semester", "SGPA", "Credits"), show="headings", height=6)
sgpa_tree.heading("Semester", text="Semester")
sgpa_tree.heading("SGPA", text="SGPA")
sgpa_tree.heading("Credits", text="Credits")
sgpa_tree.column("Semester", width=150)
sgpa_tree.column("SGPA", width=150)
sgpa_tree.column("Credits", width=150)
sgpa_tree.pack(fill="both", expand=True, padx=10, pady=10)

# Add scrollbar to treeview
scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=sgpa_tree.yview)
sgpa_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.place(relx=1, rely=0, relheight=1, anchor='ne')

# CGPA Display
cgpa_frame = ttk.Frame(results_frame)
cgpa_frame.pack(fill="x", padx=10, pady=15)

# Style the CGPA display with a box
cgpa_display_frame = tk.Frame(cgpa_frame, bg=ACCENT_COLOR, bd=1, relief="solid")
cgpa_display_frame.pack(fill="x", pady=5)

cgpa_inner_frame = tk.Frame(cgpa_display_frame, bg=ACCENT_COLOR, pady=10, padx=10)
cgpa_inner_frame.pack(fill="x")

cgpa_label = tk.Label(cgpa_inner_frame, text="CGPA: ", 
                    font=("Arial", 14, "bold"), 
                    bg=ACCENT_COLOR,
                    fg=TEXT_COLOR)
cgpa_label.pack(side="left")

cgpa_value = tk.Label(cgpa_inner_frame, text="--", 
                    font=("Arial", 14), 
                    bg=ACCENT_COLOR,
                    fg=PRIMARY_COLOR)
cgpa_value.pack(side="left")

total_credits_label = tk.Label(cgpa_inner_frame, text="Total Credits: ", 
                            font=("Arial", 12, "bold"), 
                            bg=ACCENT_COLOR,
                            fg=TEXT_COLOR, 
                            padx=20)
total_credits_label.pack(side="left")

total_credits_value = tk.Label(cgpa_inner_frame, text="--", 
                            font=("Arial", 12), 
                            bg=ACCENT_COLOR,
                            fg=PRIMARY_COLOR)
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
    
    # Calculate CGPA
    total_weighted_sgpa = sum(sgpa * credits for sgpa, credits in zip(semester_sgpas, semester_credits))
    total_all_credits = sum(semester_credits)
    
    if total_all_credits > 0:
        cgpa = total_weighted_sgpa / total_all_credits
        cgpa_value.config(text=f"{cgpa:.2f}")
        total_credits_value.config(text=f"{total_all_credits}")
    else:
        cgpa_value.config(text="--")
        total_credits_value.config(text="--")

def refresh_calculator():
    # Update the student list from the database
    global student_choices
    student_choices = populate_student_list()
    
    # Clear the student selection
    student_var.set("")
    
    # Clear the results
    for row in sgpa_tree.get_children():
        sgpa_tree.delete(row)
    
    # Reset labels
    cgpa_value.config(text="--")
    total_credits_value.config(text="--")
    
    # Show a confirmation message
    messagebox.showinfo("Refresh Complete", "Student list has been refreshed from the database.")

# Button frame for calculate and refresh buttons
calc_button_frame = ttk.Frame(calculator_frame)
calc_button_frame.pack(pady=10)

# Style the buttons
calculate_button = tk.Button(calc_button_frame, 
                            text="Calculate CGPA", 
                            command=calculate_cgpa,
                            bg=PRIMARY_COLOR,
                            fg="white",
                            font=("Arial", 11, "bold"),
                            padx=10,
                            pady=5,
                            borderwidth=0)
calculate_button.pack(side="left", padx=5)

refresh_button = tk.Button(calc_button_frame, 
                        text="Refresh", 
                        command=refresh_calculator,
                        bg=SECONDARY_COLOR,
                        fg=TEXT_COLOR,
                        font=("Arial", 11),
                        padx=10,
                        pady=5,
                        borderwidth=0)
refresh_button.pack(side="left", padx=5)

# Formula display
formula_frame = ttk.LabelFrame(calculator_frame, text="Formula Reference")
formula_frame.pack(fill="x", padx=10, pady=10)

formula_box = tk.Frame(formula_frame, bg="white", bd=1, relief="solid")
formula_box.pack(fill="x", padx=5, pady=5)

formula_text = """
SGPA Formula: SGPA = Σ(Credits × Grade Points) / Σ(Credits)
CGPA Formula: CGPA = Σ(Credits × SGPA) / Σ(Credits)

Where:
- Credits: Number of credit hours for each course
- Grade Points: Points scored in each course (usually on a scale of 0-4 or 0-10)
- SGPA: Semester Grade Point Average
- CGPA: Cumulative Grade Point Average
"""
formula_label = tk.Label(formula_box, 
                        text=formula_text, 
                        justify="left", 
                        bg="white", 
                        fg=TEXT_COLOR,
                        font=("Arial", 10),
                        padx=10, 
                        pady=10)
formula_label.pack()
# -----------------------------
# Main loop
# -----------------------------
root.mainloop()

# Close the database connection when the app exits
conn.close()