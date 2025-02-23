import random
import pandas as pd

symptoms = ["fever", "chills", "sweats", "headache", "nausea", "vomiting", "body_aches", 
            "impaired_consciousness", "prostration", "convulsions", "deep_breathing", 
            "respiratory_distress", "abnormal_bleeding", "jaundice", "severe_anemia"]
uncomplicated = symptoms[:7]
severe = symptoms[7:]
regions = {
    "Chloroquine-sensitive": ["Central America west of Panama", "Haiti", "Dominican Republic"],
    "Chloroquine-resistant": ["Sub-Saharan Africa", "Papua New Guinea", "Southeast Asia"]
}

def generate_row():
    is_severe = random.random() < 0.3
    gender = random.choice(["Male", "Female"])
    age = random.randint(1, 80)
    weight = random.randint(5, 20) if age <= 5 else random.randint(20, 40) if age <= 12 else random.randint(40, 100)
    pregnant = 1 if gender == "Female" and 15 <= age <= 45 and random.random() < 0.2 else 0
    g6pd_deficient = random.randint(0, 1) if random.random() < 0.1 else 0
    prev_meds = random.randint(0, 1) if random.random() < 0.2 else 0
    
    if is_severe:
        active_symptoms = random.sample(severe, k=random.randint(1, 3))
        drug = "IV artesunate"
        tablets_per_day = 2
        region = random.choice(regions["Chloroquine-sensitive"] + regions["Chloroquine-resistant"])
    else:
        active_symptoms = random.sample(uncomplicated, k=random.randint(1, 4))
        region_type = random.choice(["Chloroquine-sensitive", "Chloroquine-resistant"])
        region = random.choice(regions[region_type])
        if region_type == "Chloroquine-sensitive":
            drug = "Chloroquine phosphate"
            tablets_per_day = 1
        else:
            if pregnant:
                drug = "Artemether-lumefantrine"  # Safe in pregnancy
                tablets_per_day = 2
            else:
                drug = random.choice(["Artemether-lumefantrine", "Atovaquone-proguanil"])
                tablets_per_day = 2 if drug == "Artemether-lumefantrine" else 1
    
    symptom_dict = {sym: 1 if sym in active_symptoms else 0 for sym in symptoms}
    return {**symptom_dict, "Age": age, "Weight": weight, "Region": region, "Gender": gender, 
            "Pregnant": pregnant, "G6PD_Deficiency": g6pd_deficient, "Previous_Medications": prev_meds, 
            "Recommended_Drug": drug, "Tablets_Per_Day": tablets_per_day}

data = [generate_row() for _ in range(10000)]
df = pd.DataFrame(data)
df.to_csv("mDataSet.csv", index=False)