# simulation_engine.py

import pandas as pd
import numpy as np

def apply_tax(income, tax_brackets):
    tax_paid = 0
    remaining_income = income
    last_threshold = 0

    for threshold, rate in tax_brackets:
        if income > threshold:
            taxable = min(remaining_income, threshold - last_threshold)
            tax_paid += taxable * rate
            remaining_income -= taxable
            last_threshold = threshold
        else:
            break

    # Tax on remaining income above the last threshold
    if remaining_income > 0:
        tax_paid += remaining_income * tax_brackets[-1][1]

    return tax_paid

def compute_gini(array):
    # Ensure no negative income values
    array = np.clip(array, 0, None)
    array = np.sort(array)
    n = array.size
    index = np.arange(1, n + 1)
    return (np.sum((2 * index - n - 1) * array)) / (n * np.sum(array))

def simulate(policy_params, data_path):
    df = pd.read_csv(data_path)

    ubi = policy_params.get('ubi', 0)
    tax_brackets = policy_params.get('tax_brackets', [(0, 0.1), (10000, 0.2), (50000, 0.3)])
    min_wage = policy_params.get('minimum_wage', 0)

    # Calculate weekly income assuming hourly rate, capped by minimum wage if needed
    df['effective_income'] = df['pre_tax_income'] / 52  # annual to weekly
    hourly_rate = df['effective_income'] / df['hours_worked']
    hourly_rate = np.maximum(hourly_rate, min_wage)
    df['effective_income'] = hourly_rate * df['hours_worked']
    df['annual_income'] = df['effective_income'] * 52

    # Apply tax and UBI
    df['tax_paid'] = df['annual_income'].apply(lambda inc: apply_tax(inc, tax_brackets))
    df['post_tax_income'] = df['annual_income'] - df['tax_paid'] + ubi

    # Calculate outputs
    gini = compute_gini(df['post_tax_income'].values)
    avg_post_tax_income = df['post_tax_income'].mean()
    gov_deficit = (ubi * len(df)) - df['tax_paid'].sum()

    return {
        'gini': round(gini, 4),
        'avg_post_tax_income': round(avg_post_tax_income, 2),
        'gov_deficit': round(gov_deficit, 2)
    }

if __name__ == "__main__":
    # Example usage
    params = {
        'ubi': 12000,
        'tax_brackets': [(0, 0.1), (20000, 0.2), (60000, 0.3)],
        'minimum_wage': 15
    }
    results = simulate(params, "agents_sample.csv")
    print(results)
