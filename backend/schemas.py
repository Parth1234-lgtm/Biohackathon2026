from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. SHARED BASE FEATURES (Use Inheritance!)
# ==========================================
class BasePatientFeatures(BaseModel):
    age: int = Field(..., alias='Age (yrs)')
    bmi: float = Field(..., alias='BMI')
    cycle_length: int = Field(..., alias='Cycle length(days)')
    cycle_r_i: int = Field(..., alias='Cycle(R/I)')
    hair_loss: int = Field(..., alias='Hair loss(Y/N)')
    pimples: int = Field(..., alias='Pimples(Y/N)')
    fast_food: int = Field(..., alias='Fast food (Y/N)')
    reg_exercise: int = Field(..., alias='Reg.Exercise(Y/N)')
    weight_gain: int = Field(..., alias='Weight gain(Y/N)')

    model_config = {"populate_by_name": True}

# ==========================================
# 2. DOCTOR EXTENDED FEATURES 
# ==========================================
# By inheriting BasePatientFeatures, DocMlFeatures AUTOMATICALLY gets age, bmi, etc.
# No code duplication!
class DocMlFeatures(BasePatientFeatures):
    whr: float = Field(..., alias='WHR')
    msi: int = Field(..., alias='MSI')
    pulse_rate: int = Field(..., alias='Pulse rate(bpm)')
    rr: int = Field(..., alias='RR (breaths/min)')
    hb: float = Field(..., alias='Hb(g/dl)')
    pregnant: int = Field(..., alias='Pregnant(Y/N)')
    no_of_abortions: int = Field(..., alias='No. of abortions')
    fsh: float = Field(..., alias='FSH(mIU/mL)')
    lh: float = Field(..., alias='LH(mIU/mL)')
    tsh: float = Field(..., alias='TSH (mIU/L)')
    amh: float = Field(..., alias='AMH(ng/mL)')
    prl: float = Field(..., alias='PRL(ng/mL)')
    vit_d3: float = Field(..., alias='Vit D3 (ng/mL)')
    prg: float = Field(..., alias='PRG(ng/mL)')
    follicle_no_l: int = Field(..., alias='Follicle No. (L)')
    follicle_no_r: int = Field(..., alias='Follicle No. (R)')
    avg_f_size_l: float = Field(..., alias='Avg. F size (L) (mm)')
    avg_f_size_r: float = Field(..., alias='Avg. F size (R) (mm)')
    endometrium: float = Field(..., alias='Endometrium (mm)')
    skin_darkening: int = Field(..., alias='Skin darkening (Y/N)')
    hair_growth: int = Field(..., alias='hair growth(Y/N)')

# ==========================================
# 3. EXTRA SCHEMAS
# ==========================================
class BloodReport(BaseModel):
    high_protein: List[str] = Field(..., alias='high_protein') # Fixed spelling of protein!

# ==========================================
# 4. TARGETED REQUEST SCHEMAS FOR ENDPOINTS
# ==========================================
class RequestSchema(BaseModel):
    ml_features: DocMlFeatures
    blood_report: BloodReport

class ResponseSchema(BaseModel):
    diagnostic_status: str
    matched_scenario: str
    ml_probability: float
    ai_clinical_summary: dict
    pathway_graph: dict


   