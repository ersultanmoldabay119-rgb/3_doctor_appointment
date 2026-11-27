"""Практическое задание: «Запись на приём к врачу» (Tkinter)."""

import csv
import datetime
import os
import tkinter as tk
from tkinter import messagebox, ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "appointments.csv")

BG_COLOR = "#F3F6FA"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#1E293B"
ACCENT_COLOR = "#0284C7"
SUCCESS_COLOR = "#059669"
WARNING_COLOR = "#D97706"
DANGER_COLOR = "#DC2626"

MAX_COMPLAINTS_LEN = 300

DOCTORS_BY_SPECIALTY = {
    "Терапевт": [
        "Иванова Анна Сергеевна",
        "Петров Алексей Владимирович",
        "Сидорова Мария Николаевна",
    ],
    "Кардиолог": [
        "Смирнов Дмитрий Игоревич",
        "Козлова Елена Викторовна",
        "Волков Андрей Петрович",
    ],
    "Невролог": [
        "Новикова Ольга Павловна",
        "Морозов Сергей Александрович",
    ],
    "Педиатр": [
        "Фёдорова Наталья Ивановна",
        "Кузнецов Михаил Олегович",
    ],
    "Офтальмолог": [
        "Лебедева Татьяна Дмитриевна",
        "Соколов Артём Андреевич",
    ],
    "Хирург": [
        "Попов Владимир Николаевич",
        "Васильева Ирина Юрьевна",
    ],
}

TIME_SLOTS = [
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "12:30",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
    "17:00",
]

VISIT_TYPES = ["первичный", "повторный"]
VISIT_FORMATS = ["очный", "онлайн"]

STATUSES = [
    "Запланирован",
    "Пациент принят",
    "Отменён",
    "Пациент не явился",
]

STATUS_COLORS = {
    "Запланирован": "#E3F2FD",
    "Пациент принят": "#E8F5E9",
    "Отменён": "#FFEBEE",
    "Пациент не явился": "#FFF3E0",
}

CSV_FIELDS = [
    "id",
    "patient_name",
    "iin",
    "birth_date",
    "age",
    "phone",
    "email",
    "specialty",
    "doctor",
    "appointment_date",
    "appointment_time",
    "visit_type",
    "visit_format",
    "complaints",
    "status",
]


def calculate_age(birth_date: datetime.date, today: datetime.date | None = None) -> int:
    """Вычисляет полный возраст по дате рождения."""
    ref = today or datetime.date.today()
    years = ref.year - birth_date.year
    if (ref.month, ref.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def parse_date_ddmmyyyy(date_str: str) -> datetime.date | None:
    """Преобразует строку формата ДД.ММ.ГГГГ в date или возвращает None."""
    try:
        return datetime.datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def validate_appointment_data(
    patient_name: str,
    iin: str,
    birth_date_str: str,
    age_str: str,
    phone: str,
    email: str,
    specialty: str,
    doctor: str,
    appt_date_str: str,
    appt_time: str,
    visit_type: str,
    visit_format: str,
    complaints: str,
) -> tuple[bool, str]:
    """Проверяет все поля формы записи на приём."""
    if not patient_name.strip():
        return False, "Заполните поле «Ф. И. О. пациента»."

    clean_iin = iin.strip()
    if len(clean_iin) != 12 or not clean_iin.isdigit():
        return False, "ИИН должен содержать ровно 12 цифр."

    birth_date = parse_date_ddmmyyyy(birth_date_str)
    if birth_date is None:
        return False, "Введите корректную дату рождения в формате ДД.ММ.ГГГГ."

    today = datetime.date.today()
    if birth_date > today:
        return False, "Дата рождения не может быть в будущем."

    expected_age = calculate_age(birth_date, today)
    if expected_age > 125:
        return False, "Укажите реалистичную дату рождения."

    if not age_str.strip():
        return False, "Заполните поле «Возраст»."
    try:
        entered_age = int(age_str.strip())
    except ValueError:
        return False, "Возраст должен быть целым числом."

    if entered_age != expected_age:
        return (
            False,
            f"Возраст пациента ({entered_age}) не соответствует дате рождения (ожидается {expected_age}).",
        )

    clean_phone = phone.strip()
    allowed_phone_chars = set("0123456789+-() ")
    digits_count = sum(ch.isdigit() for ch in clean_phone)
    if not clean_phone or not all(ch in allowed_phone_chars for ch in clean_phone) or digits_count < 7:
        return False, "Введите корректный номер телефона (допустимы цифры и символы +, -, (, ))."

    clean_email = email.strip()
    if "@" not in clean_email or "." not in clean_email or " " in clean_email:
        return False, "Электронная почта должна содержать символы '@' и '.' без пробелов."

    if specialty not in DOCTORS_BY_SPECIALTY:
        return False, "Выберите специальность врача."

    if doctor not in DOCTORS_BY_SPECIALTY.get(specialty, []):
        return False, "Выберите врача из списка."

    appt_date = parse_date_ddmmyyyy(appt_date_str)
    if appt_date is None:
        return False, "Введите дату приёма в формате ДД.ММ.ГГГГ."
    if appt_date < today:
        return False, "Нельзя выбрать прошедшую дату приёма."

    if appt_time not in TIME_SLOTS:
        return False, "Выберите время приёма."

    if visit_type not in VISIT_TYPES:
        return False, "Выберите тип приёма (первичный или повторный)."

    if visit_format not in VISIT_FORMATS:
        return False, "Выберите формат приёма (очный или онлайн)."

    if len(complaints) > MAX_COMPLAINTS_LEN:
        return False, f"Описание жалоб не должно превышать {MAX_COMPLAINTS_LEN} символов."

    return True, ""


def find_schedule_conflict(
    records: list[dict],
    doctor: str,
    appt_date: str,
    appt_time: str,
    exclude_id: int | None = None,
) -> bool:
    """Проверяет, занято ли указанное время у врача (исключая отменённые записи)."""
    for rec in records:
        if exclude_id is not None and rec["id"] == exclude_id:
            continue
        if rec["status"] == "Отменён":
            continue
        if (
            rec["doctor"] == doctor
            and rec["appointment_date"] == appt_date
            and rec["appointment_time"] == appt_time
        ):
            return True
    return False


def get_free_slots_for_doctor(
    records: list[dict], doctor: str, appt_date: str, exclude_id: int | None = None
) -> list[str]:
    """Возвращает список свободных слотов времени у врача на выбранную дату."""
    busy = {
        rec["appointment_time"]
        for rec in records
        if (exclude_id is None or rec["id"] != exclude_id)
        and rec["status"] != "Отменён"
        and rec["doctor"] == doctor
        and rec["appointment_date"] == appt_date
    }
    return [slot for slot in TIME_SLOTS if slot not in busy]


def load_appointments_csv(file_path: str = CSV_PATH) -> list[dict]:
    """Загружает записи приёмов из CSV-файла."""
    if not os.path.exists(file_path):
        return []
    records: list[dict] = []
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            try:
                rec_id = int(row.get("id", "0"))
            except ValueError:
                continue
            records.append(
                {
                    "id": rec_id,
                    "patient_name": row.get("patient_name", ""),
                    "iin": row.get("iin", ""),
                    "birth_date": row.get("birth_date", ""),
                    "age": row.get("age", ""),
                    "phone": row.get("phone", ""),
                    "email": row.get("email", ""),
                    "specialty": row.get("specialty", ""),
                    "doctor": row.get("doctor", ""),
                    "appointment_date": row.get("appointment_date", ""),
                    "appointment_time": row.get("appointment_time", ""),
                    "visit_type": row.get("visit_type", "первичный"),
                    "visit_format": row.get("visit_format", "очный"),
                    "complaints": row.get("complaints", ""),
                    "status": row.get("status", "Запланирован"),
                }
            )
    return records


def save_appointments_csv(records: list[dict], file_path: str = CSV_PATH) -> None:
    """Сохраняет все записи приёмов в CSV-файл."""
    with open(file_path, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS, delimiter=";")
        writer.writeheader()
        for rec in records:
            writer.writerow({field: rec.get(field, "") for field in CSV_FIELDS})


class DoctorAppointmentApp:
    """Графическое приложение «Запись на приём к врачу»."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Запись на приём к врачу")
        self.root.geometry("1260x760")
        self.root.minsize(750, 550)
        self.root.configure(bg=BG_COLOR)

        self.appointments: list[dict] = []
        self.next_id = 1

        self._configure_styles()
        self._init_variables()
        self._build_ui()
        self._load_initial_data()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#E2E8F0",
            foreground=TEXT_COLOR,
        )

    def _init_variables(self) -> None:
        self.patient_name_var = tk.StringVar()
        self.iin_var = tk.StringVar()
        self.birth_date_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()

        self.specialty_var = tk.StringVar()
        self.doctor_var = tk.StringVar()

        today_str = datetime.date.today().strftime("%d.%m.%Y")
        self.appt_date_var = tk.StringVar(value=today_str)
        self.appt_time_var = tk.StringVar()
        self.visit_type_var = tk.StringVar(value="первичный")
        self.visit_format_var = tk.StringVar(value="очный")

        self.search_name_var = tk.StringVar()
        self.search_iin_var = tk.StringVar()
        self.filter_doctor_var = tk.StringVar(value="Все врачи")
        self.filter_date_var = tk.StringVar()
        self.filter_status_var = tk.StringVar(value="Все статусы")
        self.new_status_var = tk.StringVar(value="Пациент принят")

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=BG_COLOR, padx=14, pady=8)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Запись на приём к врачу",
            font=("Segoe UI", 16, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(side="left")

        main = tk.Frame(self.root, bg=BG_COLOR, padx=14, pady=4)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left_container = tk.Frame(main, bg=BG_COLOR)
        left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        canvas = tk.Canvas(left_container, bg=BG_COLOR, highlightthickness=0, width=410)
        left_scroll = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        self.form_panel = tk.Frame(canvas, bg=BG_COLOR)
        self.form_panel.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.form_panel, anchor="nw")
        canvas.configure(yscrollcommand=left_scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        left_scroll.pack(side="right", fill="y")

        right_panel = tk.Frame(main, bg=BG_COLOR)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        self._build_patient_block(self.form_panel)
        self._build_doctor_block(self.form_panel)
        self._build_datetime_block(self.form_panel)
        self._build_complaints_block(self.form_panel)
        self._build_submit_block(self.form_panel)

        self._build_filter_block(right_panel)
        self._build_table_block(right_panel)
        self._build_actions_block(right_panel)

    def _build_patient_block(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(
            parent,
            text="Данные пациента",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", pady=(0, 8))

        fields = [
            ("Ф. И. О.*:", self.patient_name_var),
            ("ИИН (12 цифр)*:", self.iin_var),
            ("Дата рождения (ДД.ММ.ГГГГ)*:", self.birth_date_var),
            ("Возраст*:", self.age_var),
            ("Телефон*:", self.phone_var),
            ("Электронная почта*:", self.email_var),
        ]
        for idx, (label, var) in enumerate(fields):
            tk.Label(
                frame, text=label, font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR, anchor="w"
            ).grid(row=idx, column=0, sticky="w", pady=3, padx=(0, 8))
            entry = tk.Entry(frame, textvariable=var, font=("Segoe UI", 9), width=24, relief="solid", bd=1)
            entry.grid(row=idx, column=1, sticky="ew", pady=3)
            if var is self.birth_date_var:
                entry.bind("<FocusOut>", lambda _e: self._autofill_age())
                entry.bind("<KeyRelease>", lambda _e: self._autofill_age())
        frame.columnconfigure(1, weight=1)

    def _autofill_age(self) -> None:
        dob = parse_date_ddmmyyyy(self.birth_date_var.get())
        if dob is not None and dob <= datetime.date.today():
            age = calculate_age(dob)
            if 0 <= age <= 125:
                self.age_var.set(str(age))

    def _build_doctor_block(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(
            parent,
            text="Выбор врача",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", pady=(0, 8))

        tk.Label(frame, text="Специальность*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=0, column=0, sticky="w", pady=3, padx=(0, 8)
        )
        self.specialty_combo = ttk.Combobox(
            frame,
            textvariable=self.specialty_var,
            values=list(DOCTORS_BY_SPECIALTY.keys()),
            state="readonly",
            font=("Segoe UI", 9),
            width=24,
        )
        self.specialty_combo.grid(row=0, column=1, sticky="ew", pady=3)
        self.specialty_combo.bind("<<ComboboxSelected>>", self._on_specialty_changed)

        tk.Label(frame, text="Врач*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=1, column=0, sticky="w", pady=3, padx=(0, 8)
        )
        self.doctor_combo = ttk.Combobox(
            frame,
            textvariable=self.doctor_var,
            values=[],
            state="readonly",
            font=("Segoe UI", 9),
            width=24,
        )
        self.doctor_combo.grid(row=1, column=1, sticky="ew", pady=3)
        frame.columnconfigure(1, weight=1)

    def _on_specialty_changed(self, _event: tk.Event | None = None) -> None:
        spec = self.specialty_var.get()
        doctors = DOCTORS_BY_SPECIALTY.get(spec, [])
        self.doctor_combo.configure(values=doctors)
        self.doctor_var.set(doctors[0] if doctors else "")

    def _build_datetime_block(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(
            parent,
            text="Дата, время и формат приёма",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            frame, text="Дата приёма (ДД.ММ.ГГГГ)*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR
        ).grid(row=0, column=0, sticky="w", pady=3, padx=(0, 8))
        tk.Entry(
            frame, textvariable=self.appt_date_var, font=("Segoe UI", 9), width=22, relief="solid", bd=1
        ).grid(row=0, column=1, sticky="ew", pady=3)

        tk.Label(frame, text="Время приёма*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=1, column=0, sticky="w", pady=3, padx=(0, 8)
        )
        ttk.Combobox(
            frame,
            textvariable=self.appt_time_var,
            values=TIME_SLOTS,
            state="readonly",
            font=("Segoe UI", 9),
            width=20,
        ).grid(row=1, column=1, sticky="ew", pady=3)

        tk.Label(frame, text="Тип приёма*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=2, column=0, sticky="w", pady=4
        )
        type_box = tk.Frame(frame, bg=CARD_BG)
        type_box.grid(row=2, column=1, sticky="w")
        for t in VISIT_TYPES:
            tk.Radiobutton(
                type_box,
                text=t.capitalize(),
                variable=self.visit_type_var,
                value=t,
                font=("Segoe UI", 9),
                bg=CARD_BG,
                fg=TEXT_COLOR,
                activebackground=CARD_BG,
            ).pack(side="left", padx=(0, 8))

        tk.Label(frame, text="Формат*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=3, column=0, sticky="w", pady=4
        )
        fmt_box = tk.Frame(frame, bg=CARD_BG)
        fmt_box.grid(row=3, column=1, sticky="w")
        for fmt in VISIT_FORMATS:
            tk.Radiobutton(
                fmt_box,
                text=fmt.capitalize(),
                variable=self.visit_format_var,
                value=fmt,
                font=("Segoe UI", 9),
                bg=CARD_BG,
                fg=TEXT_COLOR,
                activebackground=CARD_BG,
            ).pack(side="left", padx=(0, 8))

        frame.columnconfigure(1, weight=1)

    def _build_complaints_block(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(
            parent,
            text="Описание жалоб (до 300 символов)",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            padx=10,
            pady=8,
        )
        frame.pack(fill="x", pady=(0, 8))

        self.complaints_text = tk.Text(
            frame, height=4, width=42, font=("Segoe UI", 9), wrap="word", relief="solid", bd=1
        )
        self.complaints_text.pack(fill="x")
        self.complaints_text.bind("<KeyPress>", self._on_complaints_keypress)
        self.complaints_text.bind("<KeyRelease>", self._on_complaints_changed)
        self.complaints_text.bind("<<Paste>>", lambda _e: self.root.after(10, self._on_complaints_changed))

        self.complaints_counter_label = tk.Label(
            frame,
            text=f"0 / {MAX_COMPLAINTS_LEN}",
            font=("Segoe UI", 8),
            bg=CARD_BG,
            fg="#64748B",
        )
        self.complaints_counter_label.pack(anchor="e", pady=(4, 0))

    def _get_complaints_value(self) -> str:
        return self.complaints_text.get("1.0", "end-1c")

    def _on_complaints_keypress(self, event: tk.Event) -> str | None:
        allowed_keys = {
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Up",
            "Down",
            "Home",
            "End",
            "Prior",
            "Next",
            "Tab",
        }
        if event.keysym in allowed_keys or (event.state & 0x4):
            return None
        try:
            has_selection = bool(self.complaints_text.tag_ranges("sel"))
        except tk.TclError:
            has_selection = False
        if not has_selection and len(self._get_complaints_value()) >= MAX_COMPLAINTS_LEN:
            return "break"
        return None

    def _on_complaints_changed(self, _event: tk.Event | None = None) -> None:
        text = self._get_complaints_value()
        if len(text) > MAX_COMPLAINTS_LEN:
            self.complaints_text.delete(f"1.0 + {MAX_COMPLAINTS_LEN} chars", "end-1c")
            text = self._get_complaints_value()
        self.complaints_counter_label.configure(text=f"{len(text)} / {MAX_COMPLAINTS_LEN}")

    def _build_submit_block(self, parent: tk.Widget) -> None:
        btns = tk.Frame(parent, bg=BG_COLOR, pady=4)
        btns.pack(fill="x")

        tk.Button(
            btns,
            text="Записаться на приём",
            command=self.register_appointment,
            font=("Segoe UI", 10, "bold"),
            bg=SUCCESS_COLOR,
            fg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        tk.Button(
            btns,
            text="Очистить",
            command=self.clear_form,
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            fg=TEXT_COLOR,
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
        ).pack(side="left")

    def _build_filter_block(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(
            parent,
            text="Поиск и фильтрация",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            padx=10,
            pady=8,
        )
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        all_doctors = ["Все врачи"] + [
            doc for docs in DOCTORS_BY_SPECIALTY.values() for doc in docs
        ]

        tk.Label(frame, text="Ф. И. О.:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=0, column=0, sticky="w", padx=(0, 4), pady=3
        )
        e_name = tk.Entry(frame, textvariable=self.search_name_var, width=18, relief="solid", bd=1)
        e_name.grid(row=0, column=1, padx=(0, 10), pady=3, sticky="ew")
        e_name.bind("<KeyRelease>", lambda _e: self.refresh_table())

        tk.Label(frame, text="ИИН:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=0, column=2, sticky="w", padx=(0, 4), pady=3
        )
        e_iin = tk.Entry(frame, textvariable=self.search_iin_var, width=14, relief="solid", bd=1)
        e_iin.grid(row=0, column=3, padx=(0, 10), pady=3, sticky="ew")
        e_iin.bind("<KeyRelease>", lambda _e: self.refresh_table())

        tk.Label(frame, text="Дата:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=0, column=4, sticky="w", padx=(0, 4), pady=3
        )
        e_date = tk.Entry(frame, textvariable=self.filter_date_var, width=12, relief="solid", bd=1)
        e_date.grid(row=0, column=5, pady=3, sticky="ew")
        e_date.bind("<KeyRelease>", lambda _e: self.refresh_table())

        tk.Label(frame, text="Врач:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=3
        )
        doc_cb = ttk.Combobox(
            frame, textvariable=self.filter_doctor_var, values=all_doctors, state="readonly", width=22
        )
        doc_cb.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=3, sticky="ew")
        doc_cb.bind("<<ComboboxSelected>>", lambda _e: self.refresh_table())

        tk.Label(frame, text="Статус:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=1, column=3, sticky="w", padx=(0, 4), pady=3
        )
        st_cb = ttk.Combobox(
            frame,
            textvariable=self.filter_status_var,
            values=["Все статусы"] + STATUSES,
            state="readonly",
            width=18,
        )
        st_cb.grid(row=1, column=4, padx=(0, 10), pady=3, sticky="ew")
        st_cb.bind("<<ComboboxSelected>>", lambda _e: self.refresh_table())

        tk.Button(
            frame,
            text="Показать все",
            command=self.reset_filters,
            font=("Segoe UI", 9, "bold"),
            bg="#E2E8F0",
            fg=TEXT_COLOR,
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
        ).grid(row=1, column=5, sticky="e", pady=3)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(4, weight=1)

    def _build_table_block(self, parent: tk.Widget) -> None:
        frame = tk.LabelFrame(
            parent,
            text="Список записей на приём",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            padx=10,
            pady=8,
        )
        frame.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = ("patient", "doctor", "specialty", "date", "time", "format", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        spec = {
            "patient": ("Пациент", 170, "w"),
            "doctor": ("Врач", 160, "w"),
            "specialty": ("Специальность", 105, "w"),
            "date": ("Дата", 85, "center"),
            "time": ("Время", 65, "center"),
            "format": ("Формат", 75, "center"),
            "status": ("Статус", 130, "center"),
        }
        for col, (title, width, anchor) in spec.items():
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, minwidth=55, anchor=anchor)

        for status, color in STATUS_COLORS.items():
            self.tree.tag_configure(status, background=color)

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<Double-1>", lambda _e: self.show_details())

    def _build_actions_block(self, parent: tk.Widget) -> None:
        actions = tk.Frame(parent, bg=BG_COLOR)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        top_row = tk.Frame(actions, bg=BG_COLOR)
        top_row.pack(fill="x", pady=(0, 6))

        buttons = [
            ("Показать подробности", self.show_details, ACCENT_COLOR),
            ("Изменить запись", self.edit_selected, "#4F46E5"),
            ("Отменить запись", self.cancel_selected, WARNING_COLOR),
            ("Удалить запись", self.delete_selected, DANGER_COLOR),
        ]
        for idx, (text, cmd, color) in enumerate(buttons):
            tk.Button(
                top_row,
                text=text,
                command=cmd,
                font=("Segoe UI", 9, "bold"),
                bg=color,
                fg="#FFFFFF",
                relief="flat",
                padx=10,
                pady=6,
                cursor="hand2",
            ).pack(side="left", padx=(0 if idx == 0 else 6, 0))

        status_row = tk.Frame(actions, bg=CARD_BG, padx=10, pady=6)
        status_row.pack(fill="x")
        tk.Label(
            status_row,
            text="Новый статус для выбранной записи:",
            font=("Segoe UI", 9),
            bg=CARD_BG,
            fg=TEXT_COLOR,
        ).pack(side="left", padx=(0, 8))

        ttk.Combobox(
            status_row,
            textvariable=self.new_status_var,
            values=STATUSES,
            state="readonly",
            width=22,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            status_row,
            text="Изменить статус",
            command=self.change_status_selected,
            font=("Segoe UI", 9, "bold"),
            bg="#0F766E",
            fg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
        ).pack(side="left")

    def _load_initial_data(self) -> None:
        try:
            self.appointments = load_appointments_csv()
        except OSError as exc:
            messagebox.showerror(
                "Ошибка загрузки",
                f"Не удалось загрузить сохранённые записи из файла:\n{exc}",
            )
            self.appointments = []

        if self.appointments:
            self.next_id = max(r["id"] for r in self.appointments) + 1
        self.refresh_table()

    def _persist_data(self) -> bool:
        try:
            save_appointments_csv(self.appointments)
            return True
        except OSError as exc:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось сохранить записи в CSV-файл:\n{exc}",
            )
            return False

    def register_appointment(self) -> None:
        """Проверяет форму, контролирует занятость врача и добавляет запись."""
        patient_name = self.patient_name_var.get().strip()
        iin = self.iin_var.get().strip()
        birth_date = self.birth_date_var.get().strip()
        age = self.age_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        specialty = self.specialty_var.get().strip()
        doctor = self.doctor_var.get().strip()
        appt_date = self.appt_date_var.get().strip()
        appt_time = self.appt_time_var.get().strip()
        visit_type = self.visit_type_var.get().strip()
        visit_format = self.visit_format_var.get().strip()
        complaints = self._get_complaints_value().strip()

        ok, err_msg = validate_appointment_data(
            patient_name,
            iin,
            birth_date,
            age,
            phone,
            email,
            specialty,
            doctor,
            appt_date,
            appt_time,
            visit_type,
            visit_format,
            complaints,
        )
        if not ok:
            messagebox.showerror("Ошибка ввода данных", err_msg)
            return

        if find_schedule_conflict(self.appointments, doctor, appt_date, appt_time):
            free_slots = get_free_slots_for_doctor(self.appointments, doctor, appt_date)
            hint = (
                f"Свободное время на {appt_date}: {', '.join(free_slots[:6])}"
                if free_slots
                else f"На {appt_date} у этого врача нет свободного времени."
            )
            messagebox.showwarning(
                "Время занято",
                f"Врач {doctor} уже занят {appt_date} в {appt_time}.\n"
                f"Выберите другое свободное время.\n\n{hint}",
            )
            return

        record = {
            "id": self.next_id,
            "patient_name": patient_name,
            "iin": iin,
            "birth_date": birth_date,
            "age": age,
            "phone": phone,
            "email": email,
            "specialty": specialty,
            "doctor": doctor,
            "appointment_date": appt_date,
            "appointment_time": appt_time,
            "visit_type": visit_type,
            "visit_format": visit_format,
            "complaints": complaints,
            "status": "Запланирован",
        }
        self.next_id += 1
        self.appointments.append(record)
        self._persist_data()
        self.refresh_table()

        messagebox.showinfo(
            "Запись создана",
            f"Пациент {patient_name} успешно записан на приём к врачу {doctor} "
            f"({appt_date} в {appt_time}).",
        )
        self.clear_form()

    def clear_form(self) -> None:
        """Очищает поля формы после добавления или по кнопке."""
        self.patient_name_var.set("")
        self.iin_var.set("")
        self.birth_date_var.set("")
        self.age_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.specialty_var.set("")
        self.doctor_combo.configure(values=[])
        self.doctor_var.set("")
        self.appt_date_var.set(datetime.date.today().strftime("%d.%m.%Y"))
        self.appt_time_var.set("")
        self.visit_type_var.set("первичный")
        self.visit_format_var.set("очный")
        self.complaints_text.delete("1.0", "end")
        self._on_complaints_changed()

    def reset_filters(self) -> None:
        """Сбрасывает фильтры поиска и отображает все записи."""
        self.search_name_var.set("")
        self.search_iin_var.set("")
        self.filter_doctor_var.set("Все врачи")
        self.filter_date_var.set("")
        self.filter_status_var.set("Все статусы")
        self.refresh_table()

    def refresh_table(self) -> None:
        """Обновляет таблицу записей с учётом текущих фильтров и цветовых тегов."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        q_name = self.search_name_var.get().strip().casefold()
        q_iin = self.search_iin_var.get().strip()
        q_doc = self.filter_doctor_var.get()
        q_date = self.filter_date_var.get().strip()
        q_status = self.filter_status_var.get()

        for rec in self.appointments:
            if q_name and q_name not in rec["patient_name"].casefold():
                continue
            if q_iin and q_iin not in rec["iin"]:
                continue
            if q_doc != "Все врачи" and rec["doctor"] != q_doc:
                continue
            if q_date and q_date not in rec["appointment_date"]:
                continue
            if q_status != "Все статусы" and rec["status"] != q_status:
                continue

            tag = rec["status"] if rec["status"] in STATUS_COLORS else "Запланирован"
            self.tree.insert(
                "",
                "end",
                iid=str(rec["id"]),
                values=(
                    rec["patient_name"],
                    rec["doctor"],
                    rec["specialty"],
                    rec["appointment_date"],
                    rec["appointment_time"],
                    rec["visit_format"],
                    rec["status"],
                ),
                tags=(tag,),
            )

    def _get_selected_record(self) -> dict | None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Выбор записи", "Сначала выберите запись в таблице.")
            return None
        rec_id = int(sel[0])
        for rec in self.appointments:
            if rec["id"] == rec_id:
                return rec
        return None

    def show_details(self) -> None:
        """Открывает подробную информацию о выбранной записи в окне Toplevel."""
        rec = self._get_selected_record()
        if rec is None:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Подробности записи №{rec['id']}")
        win.geometry("460x440")
        win.resizable(False, False)
        win.configure(bg=CARD_BG)
        win.transient(self.root)

        body = tk.Frame(win, bg=CARD_BG, padx=18, pady=14)
        body.pack(fill="both", expand=True)

        info_rows = [
            ("Пациент:", rec["patient_name"]),
            ("ИИН:", rec["iin"]),
            ("Дата рождения:", f"{rec['birth_date']} (возраст: {rec['age']})"),
            ("Телефон:", rec["phone"]),
            ("Электронная почта:", rec["email"]),
            ("Специальность:", rec["specialty"]),
            ("Врач:", rec["doctor"]),
            ("Дата и время:", f"{rec['appointment_date']} в {rec['appointment_time']}"),
            ("Тип приёма:", rec["visit_type"]),
            ("Формат приёма:", rec["visit_format"]),
            ("Статус:", rec["status"]),
        ]
        for idx, (lbl, val) in enumerate(info_rows):
            tk.Label(
                body, text=lbl, font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR, anchor="w"
            ).grid(row=idx, column=0, sticky="w", pady=3, padx=(0, 10))
            tk.Label(
                body, text=val, font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR, anchor="w"
            ).grid(row=idx, column=1, sticky="w", pady=3)

        tk.Label(
            body, text="Жалобы:", font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR
        ).grid(row=len(info_rows), column=0, sticky="nw", pady=(6, 0))

        complaints_box = tk.Text(
            body, height=4, width=34, font=("Segoe UI", 9), wrap="word", relief="solid", bd=1
        )
        complaints_box.grid(row=len(info_rows), column=1, sticky="ew", pady=(6, 0))
        complaints_box.insert("1.0", rec["complaints"] or "Не указаны")
        complaints_box.configure(state="disabled")

        tk.Button(
            body,
            text="Закрыть",
            command=win.destroy,
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT_COLOR,
            fg="#FFFFFF",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
        ).grid(row=len(info_rows) + 1, column=0, columnspan=2, pady=(14, 0))

    def edit_selected(self) -> None:
        """Открывает окно редактирования выбранной записи."""
        rec = self._get_selected_record()
        if rec is None:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Редактирование записи №{rec['id']}")
        win.geometry("460x560")
        win.resizable(False, False)
        win.configure(bg=CARD_BG)
        win.transient(self.root)
        win.grab_set()

        p_name = tk.StringVar(value=rec["patient_name"])
        p_iin = tk.StringVar(value=rec["iin"])
        p_dob = tk.StringVar(value=rec["birth_date"])
        p_age = tk.StringVar(value=str(rec["age"]))
        p_phone = tk.StringVar(value=rec["phone"])
        p_email = tk.StringVar(value=rec["email"])
        p_spec = tk.StringVar(value=rec["specialty"])
        p_doc = tk.StringVar(value=rec["doctor"])
        p_date = tk.StringVar(value=rec["appointment_date"])
        p_time = tk.StringVar(value=rec["appointment_time"])
        p_type = tk.StringVar(value=rec["visit_type"])
        p_fmt = tk.StringVar(value=rec["visit_format"])

        form = tk.Frame(win, bg=CARD_BG, padx=16, pady=12)
        form.pack(fill="both", expand=True)

        text_rows = [
            ("Ф. И. О.*:", p_name),
            ("ИИН*:", p_iin),
            ("Дата рождения*:", p_dob),
            ("Возраст*:", p_age),
            ("Телефон*:", p_phone),
            ("Email*:", p_email),
            ("Дата приёма*:", p_date),
        ]
        for idx, (lbl, var) in enumerate(text_rows):
            tk.Label(form, text=lbl, font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
                row=idx, column=0, sticky="w", pady=3, padx=(0, 8)
            )
            e = tk.Entry(form, textvariable=var, font=("Segoe UI", 9), width=28, relief="solid", bd=1)
            e.grid(row=idx, column=1, sticky="ew", pady=3)
            if var is p_dob:
                def _sync_edit_age(_ev: tk.Event | None = None) -> None:
                    d = parse_date_ddmmyyyy(p_dob.get())
                    if d is not None and d <= datetime.date.today():
                        p_age.set(str(calculate_age(d)))

                e.bind("<KeyRelease>", _sync_edit_age)

        row_i = len(text_rows)
        tk.Label(form, text="Специальность*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=row_i, column=0, sticky="w", pady=3
        )
        spec_cb = ttk.Combobox(
            form,
            textvariable=p_spec,
            values=list(DOCTORS_BY_SPECIALTY.keys()),
            state="readonly",
            width=26,
        )
        spec_cb.grid(row=row_i, column=1, sticky="ew", pady=3)

        tk.Label(form, text="Врач*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=row_i + 1, column=0, sticky="w", pady=3
        )
        doc_cb = ttk.Combobox(
            form,
            textvariable=p_doc,
            values=DOCTORS_BY_SPECIALTY.get(p_spec.get(), []),
            state="readonly",
            width=26,
        )
        doc_cb.grid(row=row_i + 1, column=1, sticky="ew", pady=3)

        def on_edit_spec(_e: tk.Event) -> None:
            docs = DOCTORS_BY_SPECIALTY.get(p_spec.get(), [])
            doc_cb.configure(values=docs)
            p_doc.set(docs[0] if docs else "")

        spec_cb.bind("<<ComboboxSelected>>", on_edit_spec)

        tk.Label(form, text="Время*:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=row_i + 2, column=0, sticky="w", pady=3
        )
        ttk.Combobox(form, textvariable=p_time, values=TIME_SLOTS, state="readonly", width=26).grid(
            row=row_i + 2, column=1, sticky="ew", pady=3
        )

        tk.Label(form, text="Тип приёма:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=row_i + 3, column=0, sticky="w", pady=3
        )
        t_box = tk.Frame(form, bg=CARD_BG)
        t_box.grid(row=row_i + 3, column=1, sticky="w")
        for t in VISIT_TYPES:
            tk.Radiobutton(t_box, text=t, variable=p_type, value=t, bg=CARD_BG).pack(side="left")

        tk.Label(form, text="Формат:", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=row_i + 4, column=0, sticky="w", pady=3
        )
        f_box = tk.Frame(form, bg=CARD_BG)
        f_box.grid(row=row_i + 4, column=1, sticky="w")
        for f_val in VISIT_FORMATS:
            tk.Radiobutton(f_box, text=f_val, variable=p_fmt, value=f_val, bg=CARD_BG).pack(
                side="left"
            )

        tk.Label(form, text="Жалобы (до 300):", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR).grid(
            row=row_i + 5, column=0, sticky="nw", pady=3
        )
        c_text = tk.Text(form, height=4, width=28, font=("Segoe UI", 9), wrap="word", relief="solid", bd=1)
        c_text.grid(row=row_i + 5, column=1, sticky="ew", pady=3)
        c_text.insert("1.0", rec["complaints"])

        def save_edit() -> None:
            complaints_val = c_text.get("1.0", "end-1c").strip()
            ok, err = validate_appointment_data(
                p_name.get(),
                p_iin.get(),
                p_dob.get(),
                p_age.get(),
                p_phone.get(),
                p_email.get(),
                p_spec.get(),
                p_doc.get(),
                p_date.get(),
                p_time.get(),
                p_type.get(),
                p_fmt.get(),
                complaints_val,
            )
            if not ok:
                messagebox.showerror("Ошибка ввода", err, parent=win)
                return

            if find_schedule_conflict(
                self.appointments, p_doc.get(), p_date.get().strip(), p_time.get(), exclude_id=rec["id"]
            ):
                messagebox.showwarning(
                    "Время занято",
                    f"Врач {p_doc.get()} уже занят {p_date.get().strip()} в {p_time.get()}.",
                    parent=win,
                )
                return

            rec.update(
                {
                    "patient_name": p_name.get().strip(),
                    "iin": p_iin.get().strip(),
                    "birth_date": p_dob.get().strip(),
                    "age": p_age.get().strip(),
                    "phone": p_phone.get().strip(),
                    "email": p_email.get().strip(),
                    "specialty": p_spec.get(),
                    "doctor": p_doc.get(),
                    "appointment_date": p_date.get().strip(),
                    "appointment_time": p_time.get(),
                    "visit_type": p_type.get(),
                    "visit_format": p_fmt.get(),
                    "complaints": complaints_val,
                }
            )
            self._persist_data()
            self.refresh_table()
            win.destroy()
            messagebox.showinfo("Успех", "Запись успешно обновлена.")

        btn_row = tk.Frame(form, bg=CARD_BG)
        btn_row.grid(row=row_i + 6, column=0, columnspan=2, pady=(12, 0), sticky="e")
        tk.Button(
            btn_row,
            text="Сохранить изменения",
            command=save_edit,
            font=("Segoe UI", 9, "bold"),
            bg=SUCCESS_COLOR,
            fg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_row,
            text="Отмена",
            command=win.destroy,
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            fg=TEXT_COLOR,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(side="left")
        form.columnconfigure(1, weight=1)

    def cancel_selected(self) -> None:
        """Отменяет выбранную запись, изменяя её статус на «Отменён»."""
        rec = self._get_selected_record()
        if rec is None:
            return
        if rec["status"] == "Отменён":
            messagebox.showinfo("Информация", "Эта запись уже отменена.")
            return
        rec["status"] = "Отменён"
        self._persist_data()
        self.refresh_table()
        messagebox.showinfo("Статус обновлён", f"Запись пациента {rec['patient_name']} отменена.")

    def change_status_selected(self) -> None:
        """Изменяет статус выбранной записи и сразу обновляет цвет строки."""
        rec = self._get_selected_record()
        if rec is None:
            return
        new_status = self.new_status_var.get()
        if new_status not in STATUSES:
            messagebox.showerror("Ошибка", "Выберите корректный статус.")
            return
        rec["status"] = new_status
        self._persist_data()
        self.refresh_table()
        if self.tree.exists(str(rec["id"])):
            self.tree.selection_set(str(rec["id"]))

    def delete_selected(self) -> None:
        """Удаляет выбранную запись после подтверждения."""
        rec = self._get_selected_record()
        if rec is None:
            return
        if not messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить запись пациента {rec['patient_name']} ({rec['appointment_date']} {rec['appointment_time']})?",
        ):
            return
        self.appointments = [r for r in self.appointments if r["id"] != rec["id"]]
        self._persist_data()
        self.refresh_table()


def main() -> None:
    root = tk.Tk()
    DoctorAppointmentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
