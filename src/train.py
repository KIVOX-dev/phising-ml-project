import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.features import FEATURES

# load the data: 12 feature columns and the label (1 = fake, 0 = genuine)
data = pd.read_csv("dataset/phishing_domains_1000.csv")
x = data[FEATURES]
y = data["label"].map({1: "Fake", 0: "Genuine"})

# split into 80% train and 20% test
x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, random_state=42, stratify=y)

# train and check accuracy
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x_train, y_train)
print("accuracy:", accuracy_score(y_test, model.predict(x_test)))

# save it
joblib.dump(model, "models/model.pkl")
