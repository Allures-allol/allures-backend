import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Загружаем модель
model = load_model("common/models/image_classifier.h5")

# Загружаем тестовое изображение
img_path = "test_images/example.jpg"
img = image.load_img(img_path, target_size=(180, 180))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0) / 255.0  # нормализация

# Предсказание
predictions = model.predict(img_array)
predicted_class = np.argmax(predictions[0])

# Маппинг классов (должен совпадать с твоими папками)
class_names = ['art', 'automotive', 'bags', 'books', 'diy', 'electronics', 'fashion', 'food', 'home', 'medical', 'military', 'office', 'outdoor', 'personal_care', 'pets', 'sports', 'toys']
print(f"Модель предсказала класс: {class_names[predicted_class]}")
