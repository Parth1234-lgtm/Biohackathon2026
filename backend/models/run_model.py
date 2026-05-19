import joblib 
import os
import pandas as pd

model_dir=(os.path.dirname(os.path.abspath(__file__)))

doc_path=os.path.join(model_dir,"doctor_model.joblib")
doc_model=joblib.load(doc_path)


def run_model(features:dict):
    # 1. Convert the dumped dictionary to a single-row DataFrame
    df = pd.DataFrame([features])
    
    # 2. Get the probability matrix -> [[prob_of_0, prob_of_1]]
    probabilities = doc_model.predict_proba(df)
    
    # 3. Grab the first row [0], and the positive class [1]
    pcos_positive_prob = probabilities[0][1]
    
    # Return it as a clean float (perfect for handing back to FastAPI)
    return float(pcos_positive_prob)

    
