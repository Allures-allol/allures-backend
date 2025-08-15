# check_new_classes.py
import os
import json
import subprocess

DATA_DIR = "dataset"
CLASSES_FILE = "models/class_names.txt"

def get_current_classes():
    return sorted([d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))])

def load_known_classes():
    if os.path.exists(CLASSES_FILE):
        with open(CLASSES_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

def save_known_classes(class_list):
    with open(CLASSES_FILE, "w") as f:
        for class_name in class_list:
            f.write(f"{class_name}\n")

if __name__ == "__main__":
    current_classes = get_current_classes()
    known_classes = load_known_classes()

    new_classes = list(set(current_classes) - set(known_classes))

    if new_classes:
        print(f"🔔 Обнаружены новые классы: {new_classes}")
        print("🚀 Запускаем дообучение модели...")
        subprocess.run(["python", "models/train_model.py", "--fine-tune"])
        save_known_classes(current_classes)
    else:
        print("✅ Новых классов не найдено. Модель актуальна.")
