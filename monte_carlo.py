"""
monte_carlo.py
Simulates Phase II clinical drug development paths to evaluate the eNPV differences
between traditional VC strategies and AI-assisted early termination models.
"""

import numpy as np
import matplotlib.pyplot as plt

def run_simulation(n_simulations=10000):
    # Lock random seed for absolute reproducibility
    np.random.seed(42)
    
    # Empirical Parameters
    # Capital exposure derived from Tufts CSDD, DiMasi et al. (2016)
    cost_per_trial = 50  
    success_payoff = 500 
    
    # Phase II-to-III transition rate based on Wong et al. (2019)
    base_success_rate = 0.30 
    
    # AI Toxicity Prediction Assumptions
    # Conservative specificity mapped from typical ROC-AUC (0.7-0.8)
    ai_true_negative_rate = 0.60 
    early_stop_cost = 10 
    
    print(f"Running {n_simulations} clinical investment simulations...")
    
    # Traditional VC Model
    random_draws = np.random.rand(n_simulations)
    traditional_success = random_draws < base_success_rate
    traditional_returns = np.where(traditional_success, success_payoff - cost_per_trial, -cost_per_trial)
    
    # AI-Assisted VC Model
    ai_returns = np.zeros(n_simulations)
    
    for i in range(n_simulations):
        if traditional_success[i]:
            ai_returns[i] = success_payoff - cost_per_trial
        else:
            if np.random.rand() < ai_true_negative_rate:
                ai_returns[i] = -early_stop_cost 
            else:
                ai_returns[i] = -cost_per_trial  

    # Statistical Evaluation
    trad_mean = np.mean(traditional_returns)
    ai_mean = np.mean(ai_returns)
    
    print("\n--- Simulation Results ---")
    print(f"Traditional VC Average eNPV: ${trad_mean:.2f}M")
    print(f"AI-Assisted VC Average eNPV: ${ai_mean:.2f}M")
    print(f"Expected Value Added by AI: ${(ai_mean - trad_mean):.2f}M")
    
    # Visualization
    plt.figure(figsize=(12, 6))
    
    plt.hist(traditional_returns, bins=30, alpha=0.5, color='red', 
             label=f'Traditional VC (Mean: ${trad_mean:.1f}M)', density=True)
    plt.hist(ai_returns, bins=30, alpha=0.6, color='blue', 
             label=f'AI-Assisted VC (Mean: ${ai_mean:.1f}M)', density=True)
    
    plt.title('Monte Carlo Simulation: Return Distribution of Drug Development (10,000 Trials)', fontsize=14)
    plt.xlabel('Net Profit / Loss ($ Millions)', fontsize=12)
    plt.ylabel('Probability Density', fontsize=12)
    plt.axvline(trad_mean, color='darkred', linestyle='dashed', linewidth=2)
    plt.axvline(ai_mean, color='darkblue', linestyle='dashed', linewidth=2)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_simulation()