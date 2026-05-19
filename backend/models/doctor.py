import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib
import os


# 1. Load data
df = pd.read_csv(r"D:\biohack2026\Biohackathon2026\backend\models\pcos_clean.csv")

df.columns = df.columns.str.strip()


# 2. Advanced Feature Engineering for Clinicians (WHR + Lab-backed MSI)
def engineer_doctor_features(data):
    X_eng = data.copy()
    
    # Waist-to-Hip Ratio
    X_eng['WHR'] = X_eng['Waist(inch)'] / X_eng['Hip(inch)'].replace(0, np.mean(X_eng['Hip(inch)']))
    X_eng['WHR'] = X_eng['WHR'].fillna(X_eng['Waist(inch)'] / (X_eng['Hip(inch)'] + 0.001))
    
    # Lab-Backed Metabolic Strain Index (MSI)
    # Combines clinical lab results (RBS > 140 mg/dl indicates prediabetes/diabetes), 
    # weight gain, and physical markers of insulin resistance like Skin Darkening (Acanthosis Nigricans)
    rbs_high = (X_eng['RBS(mg/dl)'] > 140).fillna(False).astype(int)
    weight_gain = X_eng['Weight gain(Y/N)'].fillna(0).astype(int)
    skin_darkening = X_eng['Skin darkening (Y/N)'].fillna(0).replace(np.nan,0).astype(int)
    
    X_eng['MSI'] = rbs_high + weight_gain + skin_darkening
    return X_eng

df_doc = engineer_doctor_features(df)

# 3. Final Clinician Feature Set (Explicitly excluding Marriage Status)


df_doc_clean = df_doc[df_doc['PCOS (Y/N)'].notna()]
y_doc = df_doc_clean['PCOS (Y/N)'].astype(int)

doctor_features = [
    'Age (yrs)', 'BMI', 'WHR', 'MSI', 'Pulse rate(bpm)', 'RR (breaths/min)', 'Hb(g/dl)', 
    'Cycle length(days)', 'Cycle(R/I)', 'Pregnant(Y/N)', 'No. of abortions', 
    'FSH(mIU/mL)', 'LH(mIU/mL)', 'TSH (mIU/L)', 'AMH(ng/mL)', 'PRL(ng/mL)', 'Vit D3 (ng/mL)', 
    'PRG(ng/mL)', 'Follicle No. (L)', 'Follicle No. (R)', 'Avg. F size (L) (mm)', 
    'Avg. F size (R) (mm)', 'Endometrium (mm)', 'Skin darkening (Y/N)', 'hair growth(Y/N)', 
    'Hair loss(Y/N)', 'Pimples(Y/N)', 'Fast food (Y/N)', 'Reg.Exercise(Y/N)'
]

X_doc = df_doc_clean[doctor_features]

# 4. Pipeline Setup
continuous_cols = ['Age (yrs)', 'BMI', 'WHR', 'MSI', 'Pulse rate(bpm)', 'Hb(g/dl)', 'Cycle length(days)', 'AMH(ng/mL)', 'Follicle No. (L)', 'Follicle No. (R)']
binary_cols = [c for c in doctor_features if c not in continuous_cols]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), continuous_cols),
        ('passthrough', 'passthrough', binary_cols)
    ]
)

doctor_model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=200, max_depth=8, class_weight='balanced', random_state=42))
])

doctor_model.fit(X_doc,y_doc)

# 1. This finds the exact folder where your script lives (the models folder)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Add the proper filename with the .joblib extension
save_path = os.path.join(current_dir, "doctor_model.joblib")

# 3. Dump it
joblib.dump(doctor_model, save_path)
