import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import json
import random
import time
from datetime import datetime

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role  # 'student' or 'instructor'

class Question:
    def __init__(self, question_text, options, correct_answer):
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer

class Exam:
    def __init__(self, title, duration, questions=None):
        self.title = title
        self.duration = duration  # in minutes
        self.questions = questions if questions else []

class ExamResult:
    def __init__(self, username, exam_title, score, date):
        self.username = username
        self.exam_title = exam_title
        self.score = score
        self.date = date

class ExamSystemData:
    def __init__(self):
        self.users = []
        self.exams = []
        self.results = []
        self.load_data()

    def load_data(self):
        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")
            
        # Load users
        if os.path.exists("data/users.json"):
            with open("data/users.json", "r") as f:
                user_data = json.load(f)
                self.users = [User(u["username"], u["password"], u["role"]) for u in user_data]
        else:
            # Create default admin user
            self.users = [User("admin", "admin123", "instructor")]
            self.save_users()
        
        # Load exams
        if os.path.exists("data/exams.json"):
            with open("data/exams.json", "r") as f:
                exam_data = json.load(f)
                self.exams = []
                for e in exam_data:
                    questions = [Question(q["question_text"], q["options"], q["correct_answer"]) 
                                 for q in e["questions"]]
                    self.exams.append(Exam(e["title"], e["duration"], questions))
        
        # Load results
        if os.path.exists("data/results.json"):
            with open("data/results.json", "r") as f:
                result_data = json.load(f)
                self.results = [ExamResult(r["username"], r["exam_title"], r["score"], r["date"]) 
                                for r in result_data]

    def save_users(self):
        user_data = [{"username": u.username, "password": u.password, "role": u.role} 
                     for u in self.users]
        with open("data/users.json", "w") as f:
            json.dump(user_data, f)
    
    def save_exams(self):
        exam_data = []
        for e in self.exams:
            question_data = [{"question_text": q.question_text, "options": q.options, 
                              "correct_answer": q.correct_answer} for q in e.questions]
            exam_data.append({"title": e.title, "duration": e.duration, "questions": question_data})
        with open("data/exams.json", "w") as f:
            json.dump(exam_data, f)
    
    def save_results(self):
        result_data = [{"username": r.username, "exam_title": r.exam_title, 
                        "score": r.score, "date": r.date} for r in self.results]
        with open("data/results.json", "w") as f:
            json.dump(result_data, f)
    
    def authenticate(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                return user
        return None

    def add_user(self, username, password, role):
        # Check if username already exists
        for user in self.users:
            if user.username == username:
                return False
        
        # Add new user
        self.users.append(User(username, password, role))
        self.save_users()
        return True

    def add_exam(self, title, duration, questions):
        # Check if exam title already exists
        for exam in self.exams:
            if exam.title == title:
                return False
        
        # Add new exam
        self.exams.append(Exam(title, duration, questions))
        self.save_exams()
        return True

    def add_result(self, username, exam_title, score):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results.append(ExamResult(username, exam_title, score, date))
        self.save_results()

class OnlineExamSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Exam Management System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.data = ExamSystemData()
        self.current_user = None
        
        self.setup_login_frame()
    
    def setup_login_frame(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login frame
        login_frame = tk.Frame(self.root, bg="#f0f0f0")
        login_frame.pack(pady=100)
        
        # Title
        title_label = tk.Label(login_frame, text="Online Exam Management System", 
                              font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Username
        username_label = tk.Label(login_frame, text="Username:", bg="#f0f0f0", font=("Arial", 12))
        username_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12))
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Password
        password_label = tk.Label(login_frame, text="Password:", bg="#f0f0f0", font=("Arial", 12))
        password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Login button
        login_button = tk.Button(login_frame, text="Login", command=self.login, 
                                font=("Arial", 12), bg="#4CAF50", fg="white", width=10)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Register button
        register_button = tk.Button(login_frame, text="Register", command=self.show_register, 
                                   font=("Arial", 12), bg="#2196F3", fg="white", width=10)
        register_button.grid(row=4, column=0, columnspan=2, pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Username and password are required")
            return
        
        user = self.data.authenticate(username, password)
        if user:
            self.current_user = user
            messagebox.showinfo("Login Success", f"Welcome, {username}!")
            if user.role == "instructor":
                self.setup_instructor_dashboard()
            else:
                self.setup_student_dashboard()
        else:
            messagebox.showerror("Login Error", "Invalid username or password")
    
    def show_register(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("400x300")
        register_window.configure(bg="#f0f0f0")
        
        # Username
        username_label = tk.Label(register_window, text="Username:", bg="#f0f0f0", font=("Arial", 12))
        username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        username_entry = tk.Entry(register_window, font=("Arial", 12))
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Password
        password_label = tk.Label(register_window, text="Password:", bg="#f0f0f0", font=("Arial", 12))
        password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        password_entry = tk.Entry(register_window, show="*", font=("Arial", 12))
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Role
        role_label = tk.Label(register_window, text="Role:", bg="#f0f0f0", font=("Arial", 12))
        role_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        role_var = tk.StringVar(value="student")
        role_student = tk.Radiobutton(register_window, text="Student", variable=role_var, 
                                     value="student", bg="#f0f0f0", font=("Arial", 12))
        role_student.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        role_instructor = tk.Radiobutton(register_window, text="Instructor", variable=role_var, 
                                        value="instructor", bg="#f0f0f0", font=("Arial", 12))
        role_instructor.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Register button
        def register():
            username = username_entry.get()
            password = password_entry.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Registration Error", "Username and password are required")
                return
            
            if self.data.add_user(username, password, role):
                messagebox.showinfo("Registration Success", "User registered successfully")
                register_window.destroy()
            else:
                messagebox.showerror("Registration Error", "Username already exists")
        
        register_button = tk.Button(register_window, text="Register", command=register, 
                                   font=("Arial", 12), bg="#4CAF50", fg="white", width=10)
        register_button.grid(row=4, column=0, columnspan=2, pady=20)
    
    def setup_instructor_dashboard(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create menu frame
        menu_frame = tk.Frame(self.root, bg="#333333", height=50)
        menu_frame.pack(fill="x")
        
        # Menu buttons
        create_exam_btn = tk.Button(menu_frame, text="Create Exam", command=self.show_create_exam,
                                  font=("Arial", 12), bg="#333333", fg="white", bd=0)
        create_exam_btn.pack(side="left", padx=20, pady=10)
        
        view_exams_btn = tk.Button(menu_frame, text="View Exams", command=self.show_view_exams,
                                 font=("Arial", 12), bg="#333333", fg="white", bd=0)
        view_exams_btn.pack(side="left", padx=20, pady=10)
        
        view_results_btn = tk.Button(menu_frame, text="View Results", command=self.show_view_results,
                                   font=("Arial", 12), bg="#333333", fg="white", bd=0)
        view_results_btn.pack(side="left", padx=20, pady=10)
        
        logout_btn = tk.Button(menu_frame, text="Logout", command=self.logout,
                             font=("Arial", 12), bg="#333333", fg="white", bd=0)
        logout_btn.pack(side="right", padx=20, pady=10)
        
        # Dashboard content
        dashboard_frame = tk.Frame(self.root, bg="#f0f0f0")
        dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        welcome_label = tk.Label(dashboard_frame, text=f"Welcome, {self.current_user.username}!", 
                               font=("Arial", 18, "bold"), bg="#f0f0f0")
        welcome_label.pack(pady=20)
        
        # Stats
        stats_frame = tk.Frame(dashboard_frame, bg="white", bd=1, relief="solid")
        stats_frame.pack(fill="x", padx=50, pady=20)
        
        num_exams = len(self.data.exams)
        num_students = sum(1 for user in self.data.users if user.role == "student")
        num_results = len(self.data.results)
        
        tk.Label(stats_frame, text=f"Total Exams: {num_exams}", font=("Arial", 14), bg="white").pack(pady=10)
        tk.Label(stats_frame, text=f"Total Students: {num_students}", font=("Arial", 14), bg="white").pack(pady=10)
        tk.Label(stats_frame, text=f"Total Results: {num_results}", font=("Arial", 14), bg="white").pack(pady=10)
    
    def setup_student_dashboard(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create menu frame
        menu_frame = tk.Frame(self.root, bg="#333333", height=50)
        menu_frame.pack(fill="x")
        
        # Menu buttons
        take_exam_btn = tk.Button(menu_frame, text="Take Exam", command=self.show_take_exam,
                                font=("Arial", 12), bg="#333333", fg="white", bd=0)
        take_exam_btn.pack(side="left", padx=20, pady=10)
        
        view_results_btn = tk.Button(menu_frame, text="View Results", command=self.show_view_student_results,
                                   font=("Arial", 12), bg="#333333", fg="white", bd=0)
        view_results_btn.pack(side="left", padx=20, pady=10)
        
        logout_btn = tk.Button(menu_frame, text="Logout", command=self.logout,
                             font=("Arial", 12), bg="#333333", fg="white", bd=0)
        logout_btn.pack(side="right", padx=20, pady=10)
        
        # Dashboard content
        dashboard_frame = tk.Frame(self.root, bg="#f0f0f0")
        dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        welcome_label = tk.Label(dashboard_frame, text=f"Welcome, {self.current_user.username}!", 
                               font=("Arial", 18, "bold"), bg="#f0f0f0")
        welcome_label.pack(pady=20)
        
        # Available exams
        available_exams_label = tk.Label(dashboard_frame, text="Available Exams:", 
                                       font=("Arial", 14, "bold"), bg="#f0f0f0")
        available_exams_label.pack(pady=10, anchor="w", padx=50)
        
        exams_frame = tk.Frame(dashboard_frame, bg="white", bd=1, relief="solid")
        exams_frame.pack(fill="x", padx=50, pady=10)
        
        if not self.data.exams:
            tk.Label(exams_frame, text="No exams available", font=("Arial", 12), bg="white").pack(pady=10)
        else:
            for i, exam in enumerate(self.data.exams):
                exam_frame = tk.Frame(exams_frame, bg="white")
                exam_frame.pack(fill="x", padx=10, pady=5)
                
                tk.Label(exam_frame, text=f"{i+1}. {exam.title}", font=("Arial", 12), bg="white").pack(side="left")
                tk.Label(exam_frame, text=f"Duration: {exam.duration} minutes", 
                       font=("Arial", 12), bg="white").pack(side="left", padx=20)
                tk.Label(exam_frame, text=f"Questions: {len(exam.questions)}", 
                       font=("Arial", 12), bg="white").pack(side="left", padx=20)
    
    def logout(self):
        self.current_user = None
        self.setup_login_frame()
    
    def show_create_exam(self):
        if self.current_user.role != "instructor":
            messagebox.showerror("Error", "Only instructors can create exams")
            return
        
        create_exam_window = tk.Toplevel(self.root)
        create_exam_window.title("Create Exam")
        create_exam_window.geometry("800x600")
        create_exam_window.configure(bg="#f0f0f0")
        
        title_label = tk.Label(create_exam_window, text="Create New Exam", 
                              font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(create_exam_window, bg="#f0f0f0")
        form_frame.pack(fill="both", padx=50, pady=10)
        
        # Exam title
        title_label = tk.Label(form_frame, text="Exam Title:", bg="#f0f0f0", font=("Arial", 12))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        title_entry = tk.Entry(form_frame, font=("Arial", 12), width=40)
        title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Duration
        duration_label = tk.Label(form_frame, text="Duration (minutes):", bg="#f0f0f0", font=("Arial", 12))
        duration_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        duration_entry = tk.Entry(form_frame, font=("Arial", 12), width=10)
        duration_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Questions
        questions_label = tk.Label(form_frame, text="Questions:", bg="#f0f0f0", font=("Arial", 12))
        questions_label.grid(row=2, column=0, padx=10, pady=10, sticky="ne")
        
        questions_frame = tk.Frame(form_frame, bg="white", bd=1, relief="solid", width=500, height=300)
        questions_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        questions_frame.pack_propagate(False)
        
        questions_canvas = tk.Canvas(questions_frame, bg="white")
        questions_canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(questions_frame, orient="vertical", command=questions_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        questions_canvas.configure(yscrollcommand=scrollbar.set)
        
        questions_inner_frame = tk.Frame(questions_canvas, bg="white")
        questions_canvas.create_window((0, 0), window=questions_inner_frame, anchor="nw")
        
        questions = []
        
        def add_question():
            question_window = tk.Toplevel(create_exam_window)
            question_window.title("Add Question")
            question_window.geometry("600x400")
            question_window.configure(bg="#f0f0f0")
            
            # Question text
            q_text_label = tk.Label(question_window, text="Question:", bg="#f0f0f0", font=("Arial", 12))
            q_text_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
            q_text_entry = tk.Entry(question_window, font=("Arial", 12), width=50)
            q_text_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            # Options
            options_frame = tk.Frame(question_window, bg="#f0f0f0")
            options_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
            
            option_entries = []
            for i in range(4):
                tk.Label(options_frame, text=f"Option {i+1}:", bg="#f0f0f0", font=("Arial", 12)).grid(
                    row=i, column=0, padx=10, pady=5, sticky="e")
                option_entry = tk.Entry(options_frame, font=("Arial", 12), width=40)
                option_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                option_entries.append(option_entry)
            
            # Correct answer
            correct_label = tk.Label(question_window, text="Correct Answer:", bg="#f0f0f0", font=("Arial", 12))
            correct_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
            correct_var = tk.IntVar(value=0)
            for i in range(4):
                tk.Radiobutton(question_window, text=f"Option {i+1}", variable=correct_var, 
                               value=i, bg="#f0f0f0", font=("Arial", 12)).grid(
                    row=2+i, column=1, padx=10, pady=5, sticky="w")
            
            # Save button
            def save_question():
                question_text = q_text_entry.get()
                options = [option.get() for option in option_entries]
                correct_answer = correct_var.get()
                
                if not question_text or not all(options) or correct_answer is None:
                    messagebox.showerror("Error", "All fields are required")
                    return
                
                questions.append(Question(question_text, options, correct_answer))
                update_questions_display()
                question_window.destroy()
            
            save_button = tk.Button(question_window, text="Save Question", command=save_question, 
                                   font=("Arial", 12), bg="#4CAF50", fg="white", width=15)
            save_button.grid(row=6, column=0, columnspan=2, pady=20)
        
        def update_questions_display():
            # Clear existing questions
            for widget in questions_inner_frame.winfo_children():
                widget.destroy()
            
            if not questions:
                tk.Label(questions_inner_frame, text="No questions added yet", 
                       font=("Arial", 12), bg="white").pack(pady=10)
            else:
                for i, question in enumerate(questions):
                    question_frame = tk.Frame(questions_inner_frame, bg="white")
                    question_frame.pack(fill="x", padx=5, pady=5)
                    
                    tk.Label(question_frame, text=f"Q{i+1}: {question.question_text}", 
                           font=("Arial", 12), bg="white").pack(anchor="w")
                    
                    # Delete button
                    def make_delete_func(index):
                        return lambda: delete_question(index)
                    
                    delete_btn = tk.Button(question_frame, text="Delete", 
                                         command=make_delete_func(i),
                                         font=("Arial", 10), bg="#f44336", fg="white")
                    delete_btn.pack(side="right")
            
            questions_inner_frame.update_idletasks()
            questions_canvas.configure(scrollregion=questions_canvas.bbox("all"))
        
        def delete_question(index):
            questions.pop(index)
            update_questions_display()
        
        # Add question button
        add_question_btn = tk.Button(form_frame, text="Add Question", command=add_question, 
                                   font=("Arial", 12), bg="#2196F3", fg="white", width=15)
        add_question_btn.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        update_questions_display()
        
        # Save exam button
        def save_exam():
            title = title_entry.get()
            duration = duration_entry.get()
            
            if not title or not duration or not questions:
                messagebox.showerror("Error", "All fields are required and at least one question must be added")
                return
            
            try:
                duration = int(duration)
            except ValueError:
                messagebox.showerror("Error", "Duration must be a number")
                return
            
            if self.data.add_exam(title, duration, questions):
                messagebox.showinfo("Success", "Exam created successfully")
                create_exam_window.destroy()
            else:
                messagebox.showerror("Error", "An exam with this title already exists")
        
        save_exam_btn = tk.Button(create_exam_window, text="Save Exam", command=save_exam, 
                                 font=("Arial", 14), bg="#4CAF50", fg="white", width=15)
        save_exam_btn.pack(pady=20)
    
    def show_view_exams(self):
        if self.current_user.role != "instructor":
            messagebox.showerror("Error", "Only instructors can view exams")
            return
        
        view_exams_window = tk.Toplevel(self.root)
        view_exams_window.title("View Exams")
        view_exams_window.geometry("800x600")
        view_exams_window.configure(bg="#f0f0f0")
        
        title_label = tk.Label(view_exams_window, text="All Exams", 
                              font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        exams_frame = tk.Frame(view_exams_window, bg="white", bd=1, relief="solid")
        exams_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        if not self.data.exams:
            tk.Label(exams_frame, text="No exams available", font=("Arial", 12), bg="white").pack(pady=10)
        else:
            for i, exam in enumerate(self.data.exams):
                exam_frame = tk.Frame(exams_frame, bg="white", bd=1, relief="solid")
                exam_frame.pack(fill="x", padx=10, pady=10)
                
                tk.Label(exam_frame, text=f"{i+1}. {exam.title}", 
                       font=("Arial", 14, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
                tk.Label(exam_frame, text=f"Duration: {exam.duration} minutes", 
                       font=("Arial", 12), bg="white").pack(anchor="w", padx=10, pady=2)
                tk.Label(exam_frame, text=f"Questions: {len(exam.questions)}", 
                       font=("Arial", 12), bg="white").pack(anchor="w", padx=10, pady=2)
                
                # View questions button
                def make_view_questions_func(exam_index):
                    return lambda: self.show_exam_questions(exam_index)
                
                view_questions_btn = tk.Button(exam_frame, text="View Questions", 
                                             command=make_view_questions_func(i),
                                             font=("Arial", 12), bg="#2196F3", fg="white")
                view_questions_btn.pack(anchor="w", padx=10, pady=5)
    
    def show_exam_questions(self, exam_index):
        exam = self.data.exams[exam_index]
        
        questions_window = tk.Toplevel(self.root)
        questions_window.title(f"Questions - {exam.title}")
        questions_window.geometry("800x600")
        questions_window.configure(bg="#f0f0f0")
        
        title_label = tk.Label(questions_window, text=f"Questions for {exam.title}", 
                              font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        questions_frame = tk.Frame(questions_window, bg="white", bd=1, relief="solid")
        questions_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        canvas = tk.Canvas(questions_frame, bg="white")
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(questions_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        questions_inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=questions_inner_frame, anchor="nw")
        
        for i, question in enumerate(exam.questions):
            question_frame = tk.Frame(questions_inner_frame, bg="white", bd=1, relief="solid")
            question_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(question_frame, text=f"Q{i+1}: {question.question_text}", 
                   font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
            
            for j, option in enumerate(question.options):
                option_frame = tk.Frame(question_frame, bg="white")
                option_frame.pack(fill="x", padx=10, pady=2)
                
                if j == question.correct_answer:
                    tk.Label(option_frame, text=f"✓ {option}", 
                           font=("Arial", 12), fg="green", bg="white").pack(anchor="w", padx=20)
                else:
                    tk.Label(option_frame, text=f"  {option}", 
                           font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
        
        questions_inner_frame.update_idlet