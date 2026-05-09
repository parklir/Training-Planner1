import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

DATA_FILE = "tasks_history.json"

# Предопределённые задачи
DEFAULT_TASKS = [
    "Прочитать статью по Python",
    "Сделать зарядку 15 минут",
    "Написать план на неделю",
    "Изучить новый рецепт",
    "Позвонить родителям",
    "Разобрать рабочий стол",
    "Пройтись пешком 30 минут",
    "Выучить 5 новых слов",
    "Помыть посуду",
    "Сделать уборку в комнате"
]


# Загрузка истории
def load_history():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Сохранение истории
def save_history():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")


# Генерация случайной задачи
def generate_task():
    if not task_list:
        messagebox.showwarning("Ошибка", "Нет доступных задач. Добавьте задачи в список.")
        return

    task = random.choice(task_list)
    entry_current.delete(0, tk.END)
    entry_current.insert(0, task)

    # Добавление в историю
    task_type = task_type_var.get()
    history.append({
        "task": task,
        "type": task_type,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_history()
    update_history_table()


# Обновление таблицы истории
def update_history_table():
    for row in history_table.get_children():
        history_table.delete(row)

    filtered = history
    filter_type = filter_type_var.get()
    if filter_type != "Все":
        filtered = [h for h in history if h.get("type", "Без типа") == filter_type]

    for record in filtered:
        history_table.insert("", tk.END, values=(
            record["task"],
            record.get("type", "Без типа"),
            record["date"]
        ))


# Загрузка списка задач из файла
def load_tasks():
    global task_list
    try:
        with open("tasks.json", "r", encoding="utf-8") as f:
            task_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        task_list = DEFAULT_TASKS.copy()
    update_tasks_listbox()


# Сохранение списка задач
def save_tasks():
    try:
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(task_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить задачи: {e}")


# Обновление списка задач в Listbox
def update_tasks_listbox():
    tasks_listbox.delete(0, tk.END)
    for task in task_list:
        tasks_listbox.insert(tk.END, task)


# Добавление новой задачи
def add_task():
    new_task = entry_new_task.get().strip()
    if not new_task:
        messagebox.showwarning("Ошибка", "Введите текст задачи")
        return

    task_list.append(new_task)
    save_tasks()
    update_tasks_listbox()
    entry_new_task.delete(0, tk.END)


# Удаление выбранной задачи
def delete_task():
    selected = tasks_listbox.curselection()
    if not selected:
        messagebox.showwarning("Ошибка", "Выберите задачу для удаления")
        return

    index = selected[0]
    task_list.pop(index)
    save_tasks()
    update_tasks_listbox()


# Применить фильтр
def apply_filter():
    update_history_table()


# Сброс фильтра
def reset_filter():
    filter_type_var.set("Все")
    update_history_table()


# Очистка истории
def clear_history():
    if messagebox.askyesno("Подтверждение", "Очистить всю историю задач?"):
        history.clear()
        save_history()
        update_history_table()


# Инициализация
history = load_history()
task_list = []

# Создание окна
window = tk.Tk()
window.title("Random Task Generator")
window.geometry("600x700")

# === Генерация задачи ===
gen_frame = tk.LabelFrame(window, text="Генератор задач", padx=10, pady=10)
gen_frame.pack(fill="x", padx=10, pady=5)

tk.Label(gen_frame, text="Тип задачи:").grid(row=0, column=0, sticky="w")
task_type_var = tk.StringVar(value="Учёба")
task_type_combo = ttk.Combobox(gen_frame, textvariable=task_type_var,
                               values=["Учёба", "Спорт", "Работа", "Дом", "Другое"], width=15)
task_type_combo.grid(row=0, column=1, padx=5)

tk.Button(gen_frame, text="Сгенерировать задачу", command=generate_task, bg="green", fg="white").grid(row=1, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=10)

tk.Label(gen_frame, text="Текущая задача:").grid(row=2, column=0, sticky="w")
entry_current = tk.Entry(gen_frame, width=50, font=("Arial", 11))
entry_current.grid(row=2, column=1, padx=5)

# === Управление задачами ===
tasks_frame = tk.LabelFrame(window, text="Список доступных задач", padx=10, pady=10)
tasks_frame.pack(fill="x", padx=10, pady=5)

tasks_listbox = tk.Listbox(tasks_frame, height=6)
tasks_listbox.pack(fill="x", pady=5)

entry_new_task = tk.Entry(tasks_frame, width=50)
entry_new_task.pack(side=tk.LEFT, padx=5)

tk.Button(tasks_frame, text="Добавить", command=add_task, bg="blue", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(tasks_frame, text="Удалить", command=delete_task, bg="red", fg="white").pack(side=tk.LEFT, padx=5)

# === Фильтрация ===
filter_frame = tk.LabelFrame(window, text="Фильтрация истории", padx=10, pady=10)
filter_frame.pack(fill="x", padx=10, pady=5)

tk.Label(filter_frame, text="Тип задачи:").pack(side=tk.LEFT, padx=5)
filter_type_var = tk.StringVar(value="Все")
filter_combo = ttk.Combobox(filter_frame, textvariable=filter_type_var,
                            values=["Все", "Учёба", "Спорт", "Работа", "Дом", "Другое"], width=15)
filter_combo.pack(side=tk.LEFT, padx=5)

tk.Button(filter_frame, text="Применить", command=apply_filter).pack(side=tk.LEFT, padx=5)
tk.Button(filter_frame, text="Сбросить", command=reset_filter).pack(side=tk.LEFT, padx=5)
tk.Button(filter_frame, text="Очистить историю", command=clear_history, bg="red", fg="white").pack(side=tk.LEFT, padx=5)

# === История ===
history_frame = tk.LabelFrame(window, text="История задач", padx=10, pady=10)
history_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("task", "type", "date")
history_table = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
history_table.heading("task", text="Задача")
history_table.heading("type", text="Тип")
history_table.heading("date", text="Дата и время")
history_table.column("task", width=400)
history_table.column("type", width=100)
history_table.column("date", width=150)
history_table.pack(fill="both", expand=True)

update_history_table()
window.mainloop()