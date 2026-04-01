import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# ==============================
# 1. Load dataset
# ==============================
df = pd.read_csv("data.csv")
df = df.dropna()   # 🔥 ADD THIS LINE

print("📊 Dataset Preview:")
print(df.head())

# ==============================
# 2. Features and Target
# ==============================
X = df[["FootTemp", "OutsideTemp"]]
y = df["HeatLevel"]

# ==============================
# 3. Train-Test Split
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, shuffle=True, random_state=42
)

print("\n✅ Data split complete")
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# ==============================
# 4. Model
# ==============================
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    random_state=42
)

# ==============================
# 5. Train Model
# ==============================
model.fit(X_train, y_train)
print("\n🔥 Model training complete")
print("\n📊 Feature Importance:")
for name, val in zip(X.columns, model.feature_importances_):
    print(f"{name}: {val:.3f}")

# ==============================
# 6. Prediction
# ==============================
y_pred = model.predict(X_test)

# ==============================
# 7. Evaluation
# ==============================
print("\n✅ Accuracy:", accuracy_score(y_test, y_pred))

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

print("\n🔳 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
with open("metrics.txt", "w") as f:
    f.write(f"Accuracy: {accuracy_score(y_test, y_pred)}")

# ==============================
# 8. Save Model
# ==============================
joblib.dump(model, "model.pkl")
print("\n💾 Model saved as model.pkl")

# ==============================
# 9. Test Prediction
# ==============================
sample = pd.DataFrame([[30, 15]], columns=["FootTemp", "OutsideTemp"])
prediction = model.predict(sample)

print("\n🧪 Sample Prediction:", prediction[0])