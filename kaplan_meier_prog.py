import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt


file_path = 'Combined_Kaplan-Meier_Data_new.xlsx'
data = pd.read_excel(file_path, skiprows=0, engine='openpyxl')


if 'time' in data.columns and 'event' in data.columns and 'disease' in data.columns:
    kmf = KaplanMeierFitter()
    unique_diseases = data['disease'].unique()
    survival_functions = []

 
    for disease in unique_diseases[:10]:  
        disease_data = data[data['disease'] == disease]
        time = disease_data['time']
        event = disease_data['event']

        kmf.fit(time, event_observed=event, label=disease)
        survival_functions.append(kmf.survival_function_)
        kmf.plot_survival_function()


    mean_survival = pd.concat(survival_functions, axis=1).mean(axis=1)
    mean_survival.name = 'Mean Survival Probability'

    mean_survival_interpolated = mean_survival.reindex(range(int(mean_survival.index.min()), 
                                                             int(mean_survival.index.max()) + 1)).interpolate()

    plt.plot(mean_survival_interpolated, label='Interpolated Mean Survival Curve', linestyle='--', color='black')
    plt.title('Kaplan-Meier Curves for Each Disease with Mean Curve')
    plt.xlabel('Time')
    plt.ylabel('Survival Probability')
    plt.legend()
    plt.show()

    for i in range(10):

        year = float(input("Enter the year for which you want the survival probability (e.g., 1 for year 1): "))
        if year in mean_survival_interpolated.index:
            survival_at_year = mean_survival_interpolated.loc[year]
            print(f"The interpolated survival probability at year {year} is approximately {survival_at_year:.4f}")
        else:
            print("The requested year is out of range.")

else:
    print("The data file does not contain the necessary columns ('time', 'event', 'disease').")
