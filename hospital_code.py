import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
import re

class HospitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Больничная система")
        self.root.geometry("650x600")
        
        # Настройка цветовой гаммы
        self.setup_colors()
        
        # Центрирование окна
        self.center_window(650, 600)
        
        # Инициализация данных врачей
        self.doctors = {
            "Иванов И.И.": {
                "password": "pass1", 
                "specialty": "терапевт"
            },
            "Сидоров В.П.": {
                "password": "pass2", 
                "specialty": "хирург"
            },
            "Смирнов А.В.": {
                "password": "pass3", 
                "specialty": "кардиолог"
            },
            "Федорова Е.П.": {
                "password": "pass4", 
                "specialty": "невролог"
            }
        }
        
        # Доступное время для записи
        self.available_times = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30", "17:00"
        ]
        
        # Загрузка данных из файла
        self.load_data()
        
        # Главный фрейм
        self.main_frame = ttk.Frame(root, style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация для центрирования
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Текущий пользователь
        self.current_user = None
        self.user_type = None
        self.current_doctor_name = None
        self.current_specialty = None
        self.current_snils = None
        
        self.show_login_screen()
    
    def setup_colors(self):
        """Настройка цветовой гаммы приложения"""
        self.colors = {
            'primary': '#1E3A8A',      # Темно-синий
            'secondary': '#3B82F6',    # Ярко-синий
            'background': '#F8FAFC',   # Светлый фон
            'surface': '#FFFFFF',      # Белый для панелей
            'text': '#1E293B',         # Темный текст
            'text_light': '#64748B',   # Светлый текст
            'success': '#10B981',      # Зеленый успех
            'warning': '#F59E0B',      # Оранжевый предупреждение
            'error': '#EF4444',        # Красный ошибка
            'border': '#E2E8F0',       # Светлая граница
            'hover': '#2563EB',        # Цвет при наведении
        }
        
        # Настройка основного окна
        self.root.configure(bg=self.colors['background'])
        
        # Создание стилей
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Настройка стиля для основного фрейма
        self.style.configure('Main.TFrame', background=self.colors['background'])
        
        # Стиль для карточек
        self.style.configure('Card.TFrame', 
                           background=self.colors['surface'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'])
        
        # Стиль для меток
        self.style.configure('TLabel', 
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=('Arial', 10))
        
        self.style.configure('Title.TLabel',
                           font=('Arial', 18, 'bold'),
                           foreground=self.colors['primary'])
        
        self.style.configure('Header.TLabel',
                           font=('Arial', 16, 'bold'),
                           foreground=self.colors['primary'])
        
        self.style.configure('Subtitle.TLabel',
                           font=('Arial', 11),
                           foreground=self.colors['text_light'])
        
        # Стиль для кнопок
        self.style.configure('Primary.TButton',
                           font=('Arial', 10, 'bold'),
                           background=self.colors['primary'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           padding=10)
        
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['hover']),
                                 ('pressed', self.colors['secondary'])])
        
        self.style.configure('Secondary.TButton',
                           font=('Arial', 10),
                           background=self.colors['surface'],
                           foreground=self.colors['primary'],
                           borderwidth=1,
                           bordercolor=self.colors['primary'])
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['background'])])
        
        # Стиль для полей ввода
        self.style.configure('TEntry',
                           fieldbackground=self.colors['surface'],
                           foreground=self.colors['text'],
                           borderwidth=1,
                           bordercolor=self.colors['border'])
        
        # Стиль для Combobox
        self.style.configure('TCombobox',
                           fieldbackground=self.colors['surface'],
                           foreground=self.colors['text'],
                           background=self.colors['surface'])
        
        # Стиль для Treeview
        self.style.configure('Treeview',
                           background=self.colors['surface'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['surface'],
                           borderwidth=0)
        
        self.style.configure('Treeview.Heading',
                           background=self.colors['primary'],
                           foreground='white',
                           borderwidth=0,
                           font=('Arial', 10, 'bold'))
        
        self.style.map('Treeview',
                      background=[('selected', self.colors['secondary'])])
    
    def center_window(self, width, height):
        """Центрирование окна на экране"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_card_frame(self, parent, **kwargs):
        """Создание карточки с закругленными углами"""
        card = ttk.Frame(parent, style='Card.TFrame', **kwargs)
        return card
    
    def validate_snils(self, snils):
        """Валидация СНИЛС в формате XXX-XXX-XXX XX"""
        pattern = r'^\d{3}-\d{3}-\d{3} \d{2}$'
        if re.match(pattern, snils):
            # Проверка, что это действительно цифры
            digits = snils.replace('-', '').replace(' ', '')
            return digits.isdigit()
        return False
    
    def load_data(self):
        """Загрузка данных из файла или создание новых"""
        if os.path.exists("hospital_data.json"):
            with open("hospital_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.appointments = data.get("appointments", {})
                self.user_appointments = data.get("user_appointments", {})
                self.snils_data = data.get("snils_data", {})
                self.time_slots = data.get("time_slots", {})
        else:
            self.appointments = {}
            self.user_appointments = {}
            self.snils_data = {}
            self.time_slots = {}
            
            # Инициализация time_slots для всех врачей
            for doctor in self.doctors.keys():
                self.time_slots[doctor] = {}
                for time_slot in self.available_times:
                    self.time_slots[doctor][time_slot] = None
    
    def save_data(self):
        """Сохранение данных в файл"""
        data = {
            "appointments": self.appointments,
            "user_appointments": self.user_appointments,
            "snils_data": self.snils_data,
            "time_slots": self.time_slots
        }
        with open("hospital_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def clear_frame(self):
        """Очистка текущего фрейма"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Экран входа в систему"""
        self.clear_frame()
        
        # Центрирование содержимого
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Основная карточка
        main_card = self.create_card_frame(self.main_frame, padding=40)
        main_card.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(main_card, 
                               text="🏥 Больничная система", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Подзаголовок
        subtitle_label = ttk.Label(main_card, 
                                  text="Система записи на прием",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 40))
        
        # Фрейм для кнопок
        btn_frame = ttk.Frame(main_card, style='Card.TFrame')
        btn_frame.pack(pady=20, padx=20)
        
        # Кнопка входа как врач
        doctor_btn = ttk.Button(btn_frame, 
                               text="Войти как врач", 
                               command=self.doctor_login, 
                               style='Primary.TButton',
                               width=25)
        doctor_btn.pack(pady=10)
        
        # Кнопка входа как пациент
        patient_btn = ttk.Button(btn_frame, 
                                text="Войти как пациент", 
                                command=self.patient_login, 
                                style='Primary.TButton',
                                width=25)
        patient_btn.pack(pady=10)
    
    def doctor_login(self):
        """Вход для врача"""
        self.clear_frame()
        
        # Центрирование
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Карточка входа
        login_card = self.create_card_frame(self.main_frame, padding=30)
        login_card.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(login_card, 
                               text="Вход для врача", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Форма входа
        form_frame = ttk.Frame(login_card, style='Card.TFrame')
        form_frame.pack(pady=10, padx=20, fill='x')
        
        # Имя врача
        ttk.Label(form_frame, text="Имя врача:").grid(row=0, column=0, sticky="w", pady=10, padx=5)
        self.doctor_name_var = tk.StringVar()
        doctor_combo = ttk.Combobox(form_frame, textvariable=self.doctor_name_var,
                                   values=list(self.doctors.keys()), state="readonly", width=30)
        doctor_combo.grid(row=0, column=1, pady=10, padx=5)
        
        # Пароль
        ttk.Label(form_frame, text="Пароль:").grid(row=1, column=0, sticky="w", pady=10, padx=5)
        self.doctor_pass_var = tk.StringVar()
        doctor_pass_entry = ttk.Entry(form_frame, textvariable=self.doctor_pass_var,
                                     show="*", width=32)
        doctor_pass_entry.grid(row=1, column=1, pady=10, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(login_card, style='Card.TFrame')
        btn_frame.pack(pady=30)
        
        login_btn = ttk.Button(btn_frame, text="Войти", 
                              command=self.doctor_enter, 
                              style='Primary.TButton',
                              width=15)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Назад", 
                             command=self.show_login_screen, 
                             style='Secondary.TButton',
                             width=15)
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def doctor_enter(self):
        """Вход врача в систему"""
        doctor_name = self.doctor_name_var.get().strip()
        password = self.doctor_pass_var.get().strip()
        
        if not doctor_name or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return
        
        # Проверка учетных данных
        if doctor_name in self.doctors:
            doctor_data = self.doctors[doctor_name]
            if doctor_data["password"] == password:
                self.current_user = doctor_name
                self.user_type = "doctor"
                self.current_doctor_name = doctor_name
                self.current_specialty = doctor_data["specialty"]
                self.show_doctor_dashboard()
            else:
                messagebox.showerror("Ошибка", "Неверный пароль!")
        else:
            messagebox.showerror("Ошибка", "Врач с таким именем не найден!")
    
    def patient_login(self):
        """Вход для пациента"""
        self.clear_frame()
        
        # Центрирование
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Карточка входа
        login_card = self.create_card_frame(self.main_frame, padding=30)
        login_card.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(login_card, 
                               text="Вход для пациента", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Форма входа
        form_frame = ttk.Frame(login_card, style='Card.TFrame')
        form_frame.pack(pady=10, padx=20, fill='x')
        
        # Имя пациента
        ttk.Label(form_frame, text="Ваше имя:").grid(row=0, column=0, sticky="w", pady=10, padx=5)
        self.patient_name_var = tk.StringVar()
        patient_name_entry = ttk.Entry(form_frame, textvariable=self.patient_name_var, width=30)
        patient_name_entry.grid(row=0, column=1, pady=10, padx=5)
        
        # СНИЛС
        ttk.Label(form_frame, text="СНИЛС (XXX-XXX-XXX XX):").grid(row=1, column=0, sticky="w", pady=10, padx=5)
        self.patient_snils_var = tk.StringVar()
        patient_snils_entry = ttk.Entry(form_frame, textvariable=self.patient_snils_var, width=30)
        patient_snils_entry.grid(row=1, column=1, pady=10, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(login_card, style='Card.TFrame')
        btn_frame.pack(pady=30)
        
        login_btn = ttk.Button(btn_frame, text="Войти", 
                              command=self.patient_enter, 
                              style='Primary.TButton',
                              width=15)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Назад", 
                             command=self.show_login_screen, 
                             style='Secondary.TButton',
                             width=15)
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def patient_enter(self):
        """Вход пациента в систему"""
        patient_name = self.patient_name_var.get().strip()
        snils = self.patient_snils_var.get().strip()
        
        if not patient_name:
            messagebox.showwarning("Ошибка", "Введите ваше имя!")
            return
        
        if not snils:
            messagebox.showwarning("Ошибка", "Введите СНИЛС!")
            return
        
        # Валидация СНИЛС
        if not self.validate_snils(snils):
            messagebox.showerror("Ошибка", "Неверный формат СНИЛС!\nИспользуйте формат: XXX-XXX-XXX XX")
            return
        
        self.current_user = patient_name
        self.user_type = "patient"
        self.current_snils = snils
        
        # Сохраняем СНИЛС пациента
        self.snils_data[patient_name] = snils
        self.save_data()
        
        self.show_patient_dashboard()
    
    def show_doctor_dashboard(self):
        """Панель врача"""
        self.clear_frame()
        
        # Центрирование
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Основная карточка
        main_card = self.create_card_frame(self.main_frame, padding=30)
        main_card.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(main_card, 
                               text="Панель врача", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Завтрашняя дата
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        
        # Информация о враче
        info_text = f"Врач: {self.current_doctor_name}\nСпециальность: {self.current_specialty}\nДата: {tomorrow}"
        info_label = ttk.Label(main_card, text=info_text,
                              style='TLabel',
                              font=('Arial', 11))
        info_label.pack(pady=(0, 20))
        
        # Записи пациентов
        records_label = ttk.Label(main_card, 
                                 text="Записи пациентов на завтра:", 
                                 style='Header.TLabel',
                                 font=('Arial', 12))
        records_label.pack(pady=(0, 10))
        
        # Получаем записи для этого врача
        doctor_appointments = self.appointments.get(self.current_doctor_name, [])
        
        if not doctor_appointments:
            no_records_label = ttk.Label(main_card, 
                                        text="Нет записей на завтра", 
                                        style='Subtitle.TLabel')
            no_records_label.pack(pady=20)
        else:
            # Фрейм для Treeview
            tree_frame = ttk.Frame(main_card, style='Card.TFrame')
            tree_frame.pack(pady=10, padx=10, fill='both', expand=True)
            
            # Настройка прокрутки
            tree_scroll = ttk.Scrollbar(tree_frame)
            tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Создаем Treeview
            columns = ("№", "Пациент", "СНИЛС", "Время")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                               yscrollcommand=tree_scroll.set,
                               height=min(8, len(doctor_appointments)))
            
            tree_scroll.config(command=tree.yview)
            
            # Настройка колонок
            tree.heading("№", text="№")
            tree.heading("Пациент", text="Пациент")
            tree.heading("СНИЛС", text="СНИЛС")
            tree.heading("Время", text="Время")
            
            tree.column("№", width=40, anchor="center")
            tree.column("Пациент", width=150, anchor="w")
            tree.column("СНИЛС", width=130, anchor="w")
            tree.column("Время", width=80, anchor="center")
            
            # Заполняем данными
            for i, patient in enumerate(doctor_appointments, 1):
                snils = self.snils_data.get(patient, "Не указан")
                patient_time = "Не указано"
                
                # Находим время записи
                for time_slot, time_patient in self.time_slots[self.current_doctor_name].items():
                    if time_patient == patient:
                        patient_time = time_slot
                        break
                
                tree.insert("", "end", values=(i, patient, snils, patient_time))
            
            tree.pack(fill='both', expand=True)
        
        # Кнопка выхода
        btn_frame = ttk.Frame(main_card, style='Card.TFrame')
        btn_frame.pack(pady=20)
        
        logout_btn = ttk.Button(btn_frame, text="Выйти", 
                               command=self.logout, 
                               style='Secondary.TButton',
                               width=20)
        logout_btn.pack()
    
    def show_patient_dashboard(self):
        """Панель пациента"""
        self.clear_frame()
        
        # Центрирование
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Основная карточка
        main_card = self.create_card_frame(self.main_frame, padding=30)
        main_card.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(main_card, 
                               text="Панель пациента", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Информация о пациенте
        info_frame = ttk.Frame(main_card, style='Card.TFrame')
        info_frame.pack(pady=(0, 20), padx=20, fill='x')
        
        name_label = ttk.Label(info_frame, 
                              text=f"Пациент: {self.current_user}",
                              style='TLabel',
                              font=('Arial', 11, 'bold'))
        name_label.pack(pady=5)
        
        snils_label = ttk.Label(info_frame, 
                               text=f"СНИЛС: {self.current_snils}",
                               style='Subtitle.TLabel')
        snils_label.pack(pady=5)
        
        # Кнопки действий
        actions_frame = ttk.Frame(main_card, style='Card.TFrame')
        actions_frame.pack(pady=10, padx=20)
        
        make_appointment_btn = ttk.Button(actions_frame, 
                                         text="Записаться на прием", 
                                         command=self.show_appointment_form, 
                                         style='Primary.TButton',
                                         width=25)
        make_appointment_btn.pack(pady=10)
        
        view_appointments_btn = ttk.Button(actions_frame, 
                                          text="Мои записи", 
                                          command=self.show_my_appointments, 
                                          style='Primary.TButton',
                                          width=25)
        view_appointments_btn.pack(pady=10)
        
        # Кнопка выхода
        btn_frame = ttk.Frame(main_card, style='Card.TFrame')
        btn_frame.pack(pady=20)
        
        logout_btn = ttk.Button(btn_frame, text="Выйти", 
                               command=self.logout, 
                               style='Secondary.TButton',
                               width=20)
        logout_btn.pack()
    
    def show_appointment_form(self):
        """Форма записи на прием"""
        self.clear_frame()
        
        # Центрирование
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Карточка формы
        form_card = self.create_card_frame(self.main_frame, padding=30)
        form_card.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(form_card, 
                               text="Запись на прием", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Завтрашняя дата
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
        
        # Дата приема
        date_label = ttk.Label(form_card, 
                              text=f"Дата приема: {tomorrow}", 
                              style='TLabel',
                              font=('Arial', 11))
        date_label.pack(pady=(0, 20))
        
        # Форма выбора
        selection_frame = ttk.Frame(form_card, style='Card.TFrame')
        selection_frame.pack(pady=10, padx=20, fill='x')
        
        # Выбор врача
        ttk.Label(selection_frame, text="Выберите врача:").grid(row=0, column=0, sticky="w", pady=15, padx=10)
        self.appoint_doctor_var = tk.StringVar()
        
        doctors_list = []
        for name, data in self.doctors.items():
            doctors_list.append(f"{name} ({data['specialty']})")
        
        doctor_combo = ttk.Combobox(selection_frame, textvariable=self.appoint_doctor_var, 
                                   values=doctors_list, state="readonly", width=30)
        doctor_combo.grid(row=0, column=1, pady=15, padx=10)
        doctor_combo.bind('<<ComboboxSelected>>', self.update_time_slots)
        
        # Выбор времени
        ttk.Label(selection_frame, text="Выберите время:").grid(row=1, column=0, sticky="w", pady=15, padx=10)
        self.appoint_time_var = tk.StringVar()
        self.time_combo = ttk.Combobox(selection_frame, textvariable=self.appoint_time_var,
                                      state="readonly", width=30)
        self.time_combo.grid(row=1, column=1, pady=15, padx=10)
        self.time_combo['values'] = []
        
        # Кнопки
        btn_frame = ttk.Frame(form_card, style='Card.TFrame')
        btn_frame.pack(pady=30)
        
        appoint_btn = ttk.Button(btn_frame, text="Записаться", 
                                command=self.make_appointment, 
                                style='Primary.TButton',
                                width=15)
        appoint_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = ttk.Button(btn_frame, text="Назад", 
                             command=self.show_patient_dashboard, 
                             style='Secondary.TButton',
                             width=15)
        back_btn.pack(side=tk.LEFT, padx=5)
    
    def update_time_slots(self, event=None):
        """Обновление доступного времени при выборе врача"""
        doctor_full = self.appoint_doctor_var.get()
        if not doctor_full:
            return
        
        doctor_name = doctor_full.split(" (")[0]
        
        # Получаем занятое время
        booked_times = []
        for time_slot, patient in self.time_slots.get(doctor_name, {}).items():
            if patient is not None:
                booked_times.append(time_slot)
        
        # Фильтруем доступное время
        available_times = [time for time in self.available_times if time not in booked_times]
        
        # Обновляем комбобокс
        self.time_combo['values'] = available_times
        if available_times:
            self.time_combo.set(available_times[0])
        else:
            self.time_combo.set("Нет свободного времени")
    
    def make_appointment(self):
        """Создание записи на прием"""
        doctor_full = self.appoint_doctor_var.get()
        time_slot = self.appoint_time_var.get()
        
        if not doctor_full:
            messagebox.showwarning("Ошибка", "Выберите врача!")
            return
        
        if not time_slot or time_slot == "Нет свободного времени":
            messagebox.showwarning("Ошибка", "Выберите время!")
            return
        
        doctor_name = doctor_full.split(" (")[0]
        
        # Проверка, не записан ли уже пациент к этому врачу
        patient_appointments = self.user_appointments.get(self.current_user, [])
        if doctor_name in patient_appointments:
            messagebox.showwarning("Ошибка", "Вы уже записаны на прием к этому врачу!")
            return
        
        # Проверка, свободно ли выбранное время
        if self.time_slots.get(doctor_name, {}).get(time_slot) is not None:
            messagebox.showerror("Ошибка", "Это время уже занято! Выберите другое время.")
            return
        
        # Добавляем запись
        if doctor_name not in self.appointments:
            self.appointments[doctor_name] = []
        
        if self.current_user not in self.appointments[doctor_name]:
            self.appointments[doctor_name].append(self.current_user)
        
        if self.current_user not in self.user_appointments:
            self.user_appointments[self.current_user] = []
        
        if doctor_name not in self.user_appointments[self.current_user]:
            self.user_appointments[self.current_user].append(doctor_name)
        
        # Фиксируем время записи
        if doctor_name not in self.time_slots:
            self.time_slots[doctor_name] = {}
        
        self.time_slots[doctor_name][time_slot] = self.current_user
        
        # Сохраняем данные
        self.save_data()
        
        messagebox.showinfo("Успех", f"Вы успешно записаны к врачу {doctor_full}\nВремя: {time_slot}")
        self.show_patient_dashboard()
    
    def show_my_appointments(self):
        """Показать записи пациента"""
        self.clear_frame()
        
        # Центрирование
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Карточка записей
        records_card = self.create_card_frame(self.main_frame, padding=30)
        records_card.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        
        # Заголовок
        title_label = ttk.Label(records_card, 
                               text="Мои записи", 
                               style='Header.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Информация о пациенте
        info_label = ttk.Label(records_card, 
                              text=f"Пациент: {self.current_user}",
                              style='TLabel',
                              font=('Arial', 11))
        info_label.pack(pady=(0, 5))
        
        snils_label = ttk.Label(records_card, 
                               text=f"СНИЛС: {self.current_snils}",
                               style='Subtitle.TLabel')
        snils_label.pack(pady=(0, 20))
        
        patient_appointments = self.user_appointments.get(self.current_user, [])
        
        if not patient_appointments:
            no_appointments_label = ttk.Label(records_card, 
                                             text="У вас нет записей к врачам", 
                                             style='Subtitle.TLabel')
            no_appointments_label.pack(pady=20)
        else:
            appointments_label = ttk.Label(records_card, 
                                          text="Вы записаны к следующим врачам:", 
                                          style='TLabel',
                                          font=('Arial', 11, 'bold'))
            appointments_label.pack(pady=(0, 10))
            
            # Фрейм для списка записей
            list_frame = ttk.Frame(records_card, style='Card.TFrame')
            list_frame.pack(pady=10, padx=20, fill='both', expand=True)
            
            # Отображаем записи
            for i, doctor_name in enumerate(patient_appointments, 1):
                specialty = self.doctors.get(doctor_name, {}).get("specialty", "Неизвестно")
                
                appointment_time = "Не указано"
                for time_slot, patient in self.time_slots.get(doctor_name, {}).items():
                    if patient == self.current_user:
                        appointment_time = time_slot
                        break
                
                appointment_text = f"{i}. {doctor_name} ({specialty}) - {appointment_time}"
                appointment_label = ttk.Label(list_frame, 
                                            text=appointment_text,
                                            style='TLabel')
                appointment_label.pack(anchor="w", pady=5, padx=10)
        
        # Кнопка назад
        btn_frame = ttk.Frame(records_card, style='Card.TFrame')
        btn_frame.pack(pady=20)
        
        back_btn = ttk.Button(btn_frame, text="Назад", 
                             command=self.show_patient_dashboard, 
                             style='Secondary.TButton',
                             width=20)
        back_btn.pack()
    
    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.user_type = None
        self.current_doctor_name = None
        self.current_specialty = None
        self.current_snils = None
        self.show_login_screen()

def main():
    root = tk.Tk()
    app = HospitalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()