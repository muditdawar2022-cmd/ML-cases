# =========================
# 1. Import libraries
# =========================
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# =========================
# 2. Load dataset
# =========================
df = pd.read_csv(r"C:\Users\Mudit Dawar\capstone\CCPP_data.csv")   # rename your file to this OR update path

print("Shape:", df.shape)
print("\nColumns:", df.columns)
print("\nMissing values:\n", df.isnull().sum())

# =========================
# 3. Features & target
# =========================
X = df[['AT', 'V', 'AP', 'RH']]
y = df['PE']

# =========================
# 4. Train-test split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 5. Cross-validation setup
# =========================
cv = KFold(n_splits=5, shuffle=True, random_state=42)

# =========================
# 6. Models
# =========================
models = {
    "Linear Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ]),
    
    "Lasso": Pipeline([
        ("scaler", StandardScaler()),
        ("model", Lasso(alpha=0.1))
    ]),
    
    "Random Forest": Pipeline([
        ("model", RandomForestRegressor(n_estimators=200, random_state=42))
    ])
}

# =========================
# 7. Model comparison
# =========================
results = []

for name, model in models.items():
    rmse = -cross_val_score(
        model, X_train, y_train,
        cv=cv,
        scoring='neg_root_mean_squared_error'
    ).mean()
    
    r2 = cross_val_score(
        model, X_train, y_train,
        cv=cv,
        scoring='r2'
    ).mean()
    
    results.append((name, rmse, r2))

# Print results
print("\nModel Performance (CV):")
for r in results:
    print(f"{r[0]} → RMSE: {r[1]:.3f}, R2: {r[2]:.3f}")

# =========================
# 8. Choose best model
# =========================
best_model_name = sorted(results, key=lambda x: x[1])[0][0]
print(f"\nBest model based on RMSE: {best_model_name}")

best_model = models[best_model_name]

# =========================
# 9. Train final model
# =========================
best_model.fit(X_train, y_train)

# =========================
# 10. Test evaluation
# =========================
y_pred = best_model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\nFinal Test Results:")
print("RMSE:", round(rmse, 3))
print("R2 :", round(r2, 3))

# ==========================
# 11. Feature Importance
# ==========================
importances = best_model.named_steps['model'].feature_importances_
feature_names = X.columns

print("\nFeature Importances (Random Forest):")
for feature, score in zip(feature_names, importances):
    print(f"{feature}: {score:.3f}")

# ==========================
# 12. Retrain with top 2 features (AT, V)
# ==========================
X_top2 = df[['AT', 'V']]

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X_top2, y, test_size=0.2, random_state=42
)

best_model2 = Pipeline([
    ("model", RandomForestRegressor(n_estimators=200, random_state=42))
])

best_model2.fit(X_train2, y_train2)
y_pred2 = best_model2.predict(X_test2)

rmse2 = np.sqrt(mean_squared_error(y_test2, y_pred2))
r2_2 = r2_score(y_test2, y_pred2)

print("\nTop 2 Features (AT, V) Test Results:")
print(f"RMSE: {round(rmse2, 3)}")
print(f"R2  : {round(r2_2, 3)}")

print("\nComparison:")
print(f"All 4 features → RMSE: {round(rmse, 3)}, R2: {round(r2, 3)}")
print(f"Top 2 features → RMSE: {round(rmse2, 3)}, R2: {round(r2_2, 3)}")