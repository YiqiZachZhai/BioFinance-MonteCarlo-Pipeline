"""
data_pipeline.py
Parses raw Web of Science data, extracts Bio-Finance literature trends, 
and generates publication and geographical distributions (2010-2025).
"""

import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# NOTE: Please replace the paths below with your local directory paths if running locally.
DATA_DIR = './BioFinance_WOS_Data'
OUTPUT_FILE = './Pure_BioFinance_Data.txt'

FINANCE_KEYWORDS = [
    'valuation', 'investment', 'finance', 'financial', 
    'pricing', 'venture capital', 'real option', 'roi', 'success rate'
]

def normalize_country(country_str):
    """Standardize WOS country name variations for accurate aggregation."""
    c = country_str.upper()
    if 'USA' in c or 'UNITED STATES' in c: return 'USA'
    if 'CHINA' in c or 'PEOPLES R CHINA' in c: return 'China'
    if 'ENGLAND' in c or 'UNITED KINGDOM' in c or 'UK' in c: return 'UK'
    if 'GERMANY' in c: return 'Germany'
    return c.title()

def process_data():
    filtered_records = []
    filtered_years = []
    filtered_countries = Counter()
    
    print("Initiating WOS data pipeline...")
    file_list = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    
    # Parse and filter records
    for file in file_list:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            records = f.read().split('\nER')
            
            for record in records:
                # Direct strip without PT tag restriction to ensure data parsing
                rec = record.strip()
                if not rec: continue
                    
                # Filter by core financial terms
                if any(kw in rec.lower() for kw in FINANCE_KEYWORDS):
                    filtered_records.append(rec)
                    
                    # Extract publication year
                    py_match = re.search(r'\nPY (\d{4})', rec)
                    if py_match:
                        filtered_years.append(int(py_match.group(1)))
                    
                    # Extract unique countries per paper
                    countries_in_paper = set()
                    c1_match = re.search(r'C1 ([\s\S]*?)\n[A-Z][A-Z0-9]', rec)
                    if c1_match:
                        found = re.findall(r'\] (.*?), (.*?)\.', c1_match.group(1))
                        for item in found:
                            raw_country = item[1].split(',')[-1].strip()
                            countries_in_paper.add(normalize_country(raw_country))
                            
                    for c in countries_in_paper:
                        filtered_countries[c] += 1

    # Export validated records
    print(f"Exporting {len(filtered_records)} validated records to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("FN Clarivate Analytics Web of Science\nVR 1.0\n")
        for rec in filtered_records:
            f.write(rec + "\nER\n")
        f.write("EF\n")

    return filtered_years, filtered_countries

def plot_results(years, countries):
    print("Generating statistical visualizations...")
    plt.figure(figsize=(16, 7))

    # Trend Subplot
    year_counts = Counter(years)
    df_year = pd.DataFrame.from_dict(year_counts, orient='index', columns=['Count']).sort_index()
    df_year = df_year[(df_year.index >= 2010) & (df_year.index <= 2025)]

    plt.subplot(1, 2, 1)
    plt.plot(df_year.index, df_year['Count'], marker='o', color='#1f77b4', linewidth=2.5)
    plt.title('The Evolution of Core Bio-Finance Research (2010-2025)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Publication Year', fontsize=12)
    plt.ylabel('Number of Publications', fontsize=12)
    plt.xticks(range(2010, 2026), rotation=45) 
    plt.grid(True, linestyle='--', alpha=0.6)

    # Country Subplot
    top_10 = countries.most_common(10)
    names = [x[0] for x in top_10]
    counts = [x[1] for x in top_10]

    plt.subplot(1, 2, 2)
    bars = plt.bar(names, counts, color='#2ca02c', edgecolor='black', alpha=0.8)
    plt.title('Top 10 Countries in Core Bio-Finance (2010-2025)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Number of Unique Publications', fontsize=12)
    plt.xticks(rotation=45, ha='right')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max(counts)*0.01), int(yval), ha='center', va='bottom', fontsize=11)

    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    extracted_years, extracted_countries = process_data()
    plot_results(extracted_years, extracted_countries)