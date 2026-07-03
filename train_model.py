import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
data = pd.read_csv("student_performance_dataset.csv")

# Convert text columns to numbers
le_gender = LabelEncoder()
le_dept = LabelEncoder()
le_result = LabelEncoder()

data["Gender"] = le_gender.fit_transform(data["Gender"])
data["Department"] = le_dept.fit_transform(data["Department"])
data["Result"] = le_result.fit_transform(data["Result"])

# Features
X = data[[
    "Gender",
    "Department",
    "Attendance",
    "StudyHours",
    "InternalMarks",
    "AssignmentMarks",
    "FinalExamMarks"
]]

# Target
y = data["Result"]

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained successfully!")