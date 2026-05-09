import json
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

DATA_FILE = "trainings.json"

def load_trainings():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_trainings():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(trainings, f, ensure_ascii=False, indent=4)

def add_training():
    date = entry_date.get().strip()
    training_type = type_var.get()
    duration = entry_duration.get().strip()

    if not date or not duration:
        messagebox.showwarning("Ошибка", "Заполните все поля")
        return

    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте ДД-ММ-ГГГГ")
        return

    try:
        duration_val = float(duration)
        if duration_val <= 0:
            messagebox.showwarning("Ошибка", "Длительность должна быть положительным числом")
            return
    except ValueError:
        messagebox.showwarning("Ошибка", "Длительность должна быть числом")
        return

    trainings.append({
        "date": date,
        "type": training_type,
        "duration": duration_val
    })
    save_trainings()
    update_table()
    clear_inputs()

def clear_inputs():
    entry_date.delete(0, tk.END)
    entry_duration.delete(0, tk.END)
    type_var.set("Бег")

def update_table():
    for row in table.get_children():
        table.delete(row)

    filtered = trainings
    filter_type = filter_type_var.get()
    filter_date = entry_filter_date.get().strip()

    if filter_type != "Все":
        filtered = [t for t in filtered if t["type"] == filter_type]
    if filter_date:
        try:
            datetime.strptime(filter_date, "%d-%m-%Y")
            filtered = [t for t in filtered if t["date"] == filter_date]
        except ValueError:
            messagebox.showwarning("Ошибка", "Неверный формат даты фильтра")

    for training in filtered:
        table.insert("", tk.END, values=(
            training["date"],
            training["type"],
            training["duration"]
        ))

    update_stats()

def update_stats():
    if not trainings:
        stats_label.config(text="Всего тренировок: 0 | Общее время: 0 мин")
        return

    total = len(trainings)
    total_duration = sum(t["duration"] for t in trainings)
    stats_label.config(text=f"Всего тренировок: {total} | Общее время: {total_duration} мин")

def apply_filter():
    update_table()

def reset_filter():
    filter_type_var.set("Все")
    entry_filter_date.delete(0, tk.END)
    update_table()

def delete_selected():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Ошибка", "Выберите тренировку для удаления")
        return

    if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
        item = selected[0]
        values = table.item(item, "values")
        for i, training in enumerate(trainings):
            if training["date"] == values[0] and training["type"] == values[1] and training["duration"] == float(values[2]):
                trainings.pop(i)
                break
        save_trainings()
        update_table()

trainings = load_trainings()

window = tk.Tk()
window.title("Training Planner")
window.geometry("600x600")

# === Форма добавления ===
input_frame = tk.LabelFrame(window, text="Добавить тренировку", padx=10, pady=10)
input_frame.pack(fill="x", padx=10, pady=5)

tk.Label(input_frame, text="Дата (ДД-ММ-ГГГГ):").grid(row=0, column=0, sticky="w")
entry_date = tk.Entry(input_frame)
entry_date.grid(row=0, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, sticky="w")
type_var = tk.StringVar(value="Бег")
type_combo = ttk.Combobox(input_frame, textvariable=type_var, values=["Бег", "Велосипед", "Плавание", "Силовая", "Йога"], width=15)
type_combo.grid(row=1, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w")
entry_duration = tk.Entry(input_frame)
entry_duration.grid(row=2, column=1, padx=5, pady=2)

tk.Button(input_frame, text="Добавить тренировку", command=add_training, bg="green", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

# === Фильтрация ===
filter_frame = tk.LabelFrame(window, text="Фильтрация", padx=10, pady=10)
filter_frame.pack(fill="x", padx=10, pady=5)

tk.Label(filter_frame, text="Тип:").pack(side=tk.LEFT, padx=5)
filter_type_var = tk.StringVar(value="Все")
filter_type_combo = ttk.Combobox(filter_frame, textvariable=filter_type_var, values=["Все", "Бег", "Велосипед", "Плавание", "Силовая", "Йога"], width=12)
filter_type_combo.pack(side=tk.LEFT, padx=5)

tk.Label(filter_frame, text="Дата:").pack(side=tk.LEFT, padx=5)
entry_filter_date = tk.Entry(filter_frame, width=12)
entry_filter_date.pack(side=tk.LEFT, padx=5)

tk.Button(filter_frame, text="Применить", command=apply_filter).pack(side=tk.LEFT, padx=5)
tk.Button(filter_frame, text="Сбросить", command=reset_filter).pack(side=tk.LEFT, padx=5)

# === Таблица ===
table_frame = tk.LabelFrame(window, text="Список тренировок", padx=10, pady=10)
table_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("date", "type", "duration")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
table.heading("date", text="Дата")
table.heading("type", text="Тип")
table.heading("duration", text="Длительность (мин)")
table.column("date", width=100)
table.column("type", width=120)
table.column("duration", width=100)
table.pack(fill="both", expand=True)

# === Кнопка удаления и статистика ===
bottom_frame = tk.Frame(window)
bottom_frame.pack(fill="x", padx=10, pady=5)

tk.Button(bottom_frame, text="Удалить выбранную", command=delete_selected, bg="red", fg="white").pack(side=tk.LEFT, padx=5)

stats_label = tk.Label(bottom_frame, text="", font=("Arial", 10))
stats_label.pack(side=tk.RIGHT, padx=5)

update_table()
window.mainloop()