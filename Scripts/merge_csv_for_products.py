import pandas as pd

# 1. Загрузи CSV-файлы
df1 = pd.read_csv('images_grouped_by_subcategories_utf8bom.csv')
df2 = pd.read_csv('images_with_categories.csv')
df3 = pd.read_csv('fashion-dataset/images.csv')
df4 = pd.read_csv('fashion-dataset/styles.csv')

# 2. Объединение по id (если поле так называется)
merged = pd.merge(df3, df4, on='id', how='inner')

# 3. Сохрани результат
merged.to_csv('merged_fashion_dataset.csv', index=False, encoding='utf-8-sig')
print(" Файл 'merged_fashion_dataset.csv' создан.")
