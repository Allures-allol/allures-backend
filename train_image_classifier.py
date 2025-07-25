from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import save_model
import os

# Путь к изображениям (категории = подпапки)
dataset_path = "mock_static/product-images/"

# Размер изображений и гиперпараметры
img_size = (180, 180)
batch_size = 32
epochs = 10

# Загрузка данных
train_ds = image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
)

val_ds = image_dataset_from_directory(
    dataset_path,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
)

class_names = train_ds.class_names
print("✅ Классы категорий:", class_names)

# Простая сверточная нейросеть
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(img_size[0], img_size[1], 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(len(class_names), activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# Обучение модели
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    callbacks=[EarlyStopping(patience=3)]
)

# Сохранение обученной модели
model_path = "common/models/image_classifier.h5"
model.save(model_path)
print(f"✅ Модель успешно сохранена в {model_path}")
