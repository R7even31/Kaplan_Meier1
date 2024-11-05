import pandas as pd
from lifelines import KaplanMeierFitter
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import os


output_file = 'Multiplication_Curve_Characteristics.xlsx'
file_path = 'Combined_Kaplan-Meier_Data_new.xlsx'
data = pd.read_excel(file_path, skiprows=0, engine='openpyxl')

# Check for necessary columns
if 'time' in data.columns and 'event' in data.columns and 'disease' in data.columns:
    kmf = KaplanMeierFitter()
    unique_diseases = data['disease'].unique()
    extrapolated_survivals = pd.DataFrame()

    # User input for selecting diseases to include in the multiplication curve
    selected_diseases = []
    print("Available diseases:", unique_diseases[:10])
    for disease in unique_diseases[:10]:
        while True:
            include = input(f"Do you want to include '{disease}' in the multiplication curve? (yes/no): ").strip().lower()
            if include in ['yes', 'no']:
                if include == 'yes':
                    selected_diseases.append(disease)
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    # Add censored data for each disease individually
    censored_entries = 5  # Number of censored entries per disease
    for disease in unique_diseases[:10]:
        additional_censored_data = pd.DataFrame({
            'time': [20] * censored_entries,  # Time of last observation (20 years)
            'event': [0] * censored_entries,  # Mark as censored (no event occurred)
            'disease': [disease] * censored_entries  # Assign to current disease
        })
        data = pd.concat([data, additional_censored_data], ignore_index=True)

    # Fit Kaplan-Meier curves and extrapolate for selected diseases only
    for disease in selected_diseases:  
        disease_data = data[data['disease'] == disease]
        time = disease_data['time']
        event = disease_data['event']

        kmf.fit(time, event_observed=event, label=disease)
        survival_function = kmf.survival_function_

        # Interpolate and extrapolate each selected disease's survival curve
        survival_interpolated = survival_function.reindex(
            range(int(survival_function.index.min()), int(survival_function.index.max()) + 1)
        ).interpolate()

        # Exponential decay function for extrapolation
        def exp_decay(x, a, b):
            return a * np.exp(-b * x)

        # Use the last 5 years of data (e.g., years 15-20) to fit the exponential decay
        last_years = survival_interpolated[survival_interpolated.index >= 15]
        popt, _ = curve_fit(exp_decay, last_years.index, last_years.values.flatten(), maxfev=1000)

        # Generate extrapolated values from 21 to 50 years
        extrapolated_times = np.arange(21, 51)
        extrapolated_values = exp_decay(extrapolated_times, *popt)
        extrapolated_values = np.clip(extrapolated_values, 0, None)

        # Combine observed and extrapolated data
        survival_extended = pd.concat([
            survival_interpolated,
            pd.Series(extrapolated_values, index=extrapolated_times, name=disease)
        ])
        
        extrapolated_survivals[disease] = survival_extended

        # Plot individual disease curve
        plt.plot(survival_extended, label=f"{disease} Survival Curve")

    # Calculate the multiplication curve for the selected diseases
    multiplication_curve = extrapolated_survivals[selected_diseases].prod(axis=1)

    # Plot the multiplication curve
    selected_diseases_str = ", ".join(selected_diseases)
    plt.plot(multiplication_curve, label='Multiplication Curve of Selected Diseases', linestyle='--', color='blue')
    plt.title(f'Combined Survival Curve (Multiplication of Selected Diseases: {selected_diseases_str})')
    plt.xlabel('Time')
    plt.ylabel('Survival Probability')
    plt.legend()
    plt.show()

    # Extract characteristic points every 5 years from 0 to 50
    characteristic_points = {year: multiplication_curve.get(year, np.nan) for year in range(0, 51, 5)}
    characteristic_points[0] = 1  # Set survival probability at time 0 to 1
    characteristic_df = pd.DataFrame.from_dict(characteristic_points, orient='index', columns=['Survival Probability'])
    characteristic_df.index.name = 'Time (years)'

    # Delete existing file if present and save new characteristic points
    if os.path.exists(output_file):
        os.remove(output_file)
    characteristic_df.to_excel(output_file)

    print(f"Characteristic points saved to {output_file}")

    # User input for survival probability at specific times
    for i in range(10):
        year = float(input("Enter the year for which you want the survival probability (e.g., 1 for year 1): "))
        if year in multiplication_curve.index:
            survival_at_year = multiplication_curve.loc[year]
            print(f"The combined survival probability at year {year} is approximately {survival_at_year:.4f}")
        else:
            print("The requested year is out of range.")

else:
    print("The data file does not contain the necessary columns ('time', 'event', 'disease').")
