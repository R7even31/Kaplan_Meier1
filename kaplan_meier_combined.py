
import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt


file_path = 'Combined_Kaplan-Meier_Data_new.xlsx'
data = pd.read_excel(file_path, skiprows=0, engine='openpyxl')


if 'time' in data.columns and 'event' in data.columns and 'disease' in data.columns:
    
    kmf = KaplanMeierFitter()

    
    unique_diseases = data['disease'].unique()

    
    km_models = {}
    patient_counts = {}

   
    for disease in unique_diseases:
        
        disease_data = data[data['disease'] == disease]
        time = disease_data['time']
        event = disease_data['event']
       

        
        kmf.fit(time, event_observed=event, label=disease)
        km_models[disease] = kmf.survival_function_

        
        patient_counts[disease] = len(disease_data)
        
        
        kmf.plot_survival_function()
     

    plt.title('Kaplan-Meier Curves for Each Disease')
    plt.xlabel('Time')
    plt.ylabel('Survival Probability')
    plt.show()

    
    total_patients = sum(patient_counts.values())
    
    
    combined_curve = pd.DataFrame()
    for disease, curve in km_models.items():
        weight = patient_counts[disease] / total_patients
        if combined_curve.empty:
            combined_curve = curve * weight
        else:
            combined_curve = combined_curve.add(curve * weight, fill_value=0)

    
    plt.plot(combined_curve, label='Combined Survival Curve')
    plt.title('Combined Kaplan-Meier Survival Curve (Weighted by Patient Count)')
    plt.xlabel('Time')
    plt.ylabel('Survival Probability')
    plt.legend()
    plt.show()

else:
    print("Error: 'time', 'event', and/or 'disease' columns not found in the dataset")
