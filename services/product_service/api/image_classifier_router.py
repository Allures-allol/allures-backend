# services/product_service/api/image_classifier_router.py
# services/product_service/api/image_classifier_router.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import shutil
import os

router = APIRouter()
model = load_model("common/models/image_classifier.h5")

# Категории должны соответствовать порядку, с которым обучалась модель
class_names = [
    'art', 'automotive', 'bags', 'books', 'diy', 'electronics', 'fashion',
    'food', 'home', 'medical', 'military', 'office', 'outdoor',
    'personal_care', 'pets', 'sports', 'toys'
]

# Отображение категорий в расширенной форме с подкатегорией и типом товара
CATEGORY_DETAILS = {
    'art': ('art', 'Drawing', 'Sketchbooks'),
    'automotive': ('automotive', 'Accessories', 'Car Mats'),
    'bags': ('bags', 'Accessories', 'Bags'),
    'books': ('books', 'Genres', 'Fiction'),
    'diy': ('diy', 'Tools', 'Hammer'),
    'electronics': ('gadgets', 'Tech', 'Smartwatch'),
    'fashion': ('fashion', 'Apparel', 'Clothing'),
    'food': ('food', 'Grocery', 'Snacks'),
    'home': ('home', 'Interior', 'Decor'),
    'medical': ('medical', 'Care', 'Thermometer'),
    'military': ('military', 'Uniforms', 'Boots'),
    'office': ('office', 'Stationery', 'Pens'),
    'outdoor': ('outdoor', 'Camping', 'Tents'),
    'personal_care': ('personal_care', 'Makeup', 'Lipstick'),
    'pets': ('pets', 'Care', 'Bowls'),
    'sports': ('sports', 'Training', 'Dumbbells'),
    'toys': ('toys', 'Outdoor', 'Toys'),
}

@router.post("/predict-category/")
async def predict_category(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        temp_path = f"temp_images/{file.filename}"
        os.makedirs("temp_images", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(contents)

        img = image.load_img(temp_path, target_size=(180, 180))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        predictions = model.predict(img_array)
        predicted_class = class_names[np.argmax(predictions[0])]

        category_name, subcategory, product_type = CATEGORY_DETAILS.get(predicted_class, (predicted_class, None, None))

        return {
            "predicted_category": predicted_class,
            "category_name": category_name,
            "subcategory": subcategory,
            "product_type": product_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
