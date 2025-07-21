import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# JSON dosyasını oku
with open("ruzgar_enerjisi_verisi (1).json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Özellikler ve hedef değişken
X = df[["lat", "lon"]].values
y = df["bolge"]

# Etiketleri sayısal değere çevir
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Veriyi eğitim ve test olarak ayır
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Random Forest modelini tanımla ve eğit
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Tahmin yap
y_pred = model.predict(X_test)

# Başarı oranı
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nSınıflandırma Raporu:\n", classification_report(
    y_test, y_pred,
    labels=le.transform(le.classes_),
    target_names=le.classes_,
    zero_division=0
))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Modeli ve etiketleyiciyi kaydet
joblib.dump(model, "bolge_tahmin_modeli.pkl")
np.save("label_encoder_classess.npy", le.classes_)
