import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_csv('dataset/retail_store_inventory.csv')

# Parse date and add time-based features
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayOfWeek'] = df['Date'].dt.dayofweek

# Define categorical columns (excluding 'Store ID')
categorical_cols = ['Product ID', 'Category', 'Region',
                    'Weather Condition', 'Seasonality', 'Holiday/Promotion']

# Initialize and apply OrdinalEncoders
encoders = {}
for col in categorical_cols:
    oe = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    df[[col]] = oe.fit_transform(df[[col]])
    encoders[col] = oe

# Prepare features and target
X = df.drop(columns=['Units Sold', 'Date', 'Store ID', 'Units Ordered'])
y = df['Units Sold']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\n🧠 Features used in model:\n", X.columns.tolist())

# Initialize and train the model
model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

# Evaluate on test set
y_pred = model.predict(X_test)
test_r2 = r2_score(y_test, y_pred)
test_mse = mean_squared_error(y_test, y_pred)
test_mae = mean_absolute_error(y_test, y_pred)

# Evaluate on training set to check overfitting
train_r2 = model.score(X_train, y_train)

# 5-Fold Cross-Validation
cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')

# Output evaluation
print("\n📈 Model Evaluation:")
print(f"Train R²: {train_r2:.4f}")
print(f"Test  R²: {test_r2:.4f}")
print(f"Test  MSE: {test_mse:.2f}")
print(f"Test  MAE: {test_mae:.2f}")
print(f"5-Fold Cross-Validated R² Scores: {cv_scores}")
print(f"Mean Cross-Validated R²: {np.mean(cv_scores):.4f}")

# Save model and encoders
joblib.dump(model, 'models/xgb_demand_forecasting_model.pkl')
joblib.dump(encoders, 'models/ordinal_encoders.pkl')

print("\n✅ Model and encoders saved successfully.")

# === Feature Importance Plot ===
print("\n📊 Plotting Feature Importances...")

# Get feature importances
feature_importances = model.feature_importances_
feature_names = X.columns

# Create DataFrame
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)

# Plot
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', hue='Feature', data=importance_df, palette='viridis', legend=False)
plt.title('XGBoost Feature Importance')
plt.xlabel('Importance Score')
plt.ylabel('Feature')
plt.tight_layout()
plt.show()

# Add the target column temporarily for correlation
corr_df = X.copy()
corr_df['Units Sold'] = y

# Compute the correlation matrix
corr_matrix = corr_df.corr()

# Plot the heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title("📊 Feature Correlation Heatmap")
plt.tight_layout()
plt.show()