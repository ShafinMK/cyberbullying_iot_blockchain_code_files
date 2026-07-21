#!/usr/bin/env python3
"""
Visualization Script for Blockchain Performance Results
Creates publication-quality figures for the manuscript
"""

import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

# Set style for publication
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

# Define colors
COLORS = {
    'add_evidence': '#2ecc71',
    'retrieve_evidence': '#3498db',
    'update_evidence': '#e74c3c',
    'query_forensic_doc': '#f39c12',
    'cpu_low': '#2ecc71',
    'cpu_medium': '#f39c12',
    'cpu_high': '#e74c3c'
}

def load_simulated_data():
    """Load simulated performance data (replace with actual data)"""
    
    # Throughput data (TPS)
    tps_data = {
        'Transaction Type': [
            'Add Evidence', 'Retrieve Evidence', 'Update Evidence',
            'Query Forensic Doc', 'Get Analysis', 'Get Data',
            'Acquire Data', 'Create Forensic Doc', 'Add Analysis'
        ],
        'Throughput (TPS)': [156, 304, 128, 327, 313, 363, 211, 166, 161],
        'Success Rate (%)': [99.8, 99.9, 99.7, 99.9, 99.9, 99.9, 99.8, 99.7, 99.8]
    }
    
    # Latency data (ms)
    latency_data = {
        'Transaction Type': [
            'Add Evidence', 'Retrieve Evidence', 'Update Evidence',
            'Query Forensic Doc', 'Get Analysis', 'Get Data',
            'Acquire Data', 'Create Forensic Doc', 'Add Analysis'
        ],
        'Avg Latency (ms)': [255, 112, 327, 98, 145, 89, 187, 289, 272],
        'Max Latency (ms)': [421, 203, 489, 167, 267, 194, 290, 472, 486],
        'Min Latency (ms)': [134, 67, 178, 45, 78, 34, 98, 156, 145]
    }
    
    # CPU usage data across Fabric versions
    cpu_data = {
        'Version': ['v2.2', 'v2.3', 'v2.4', 'v2.5'],
        'Low Load': [28, 24, 20, 16],
        'Medium Load': [47, 40, 33, 27],
        'High Load': [92, 78, 65, 53]
    }
    
    return tps_data, latency_data, cpu_data

def create_throughput_plot(tps_data, save_path='../figures/throughput.png'):
    """Create throughput comparison plot"""
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Sort by throughput
    df = pd.DataFrame(tps_data)
    df = df.sort_values('Throughput (TPS)', ascending=True)
    
    # Create horizontal bar chart
    bars = ax.barh(df['Transaction Type'], df['Throughput (TPS)'], 
                  color=sns.color_palette("viridis", len(df)))
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 5, bar.get_y() + bar.get_height()/2,
               f'{width:.0f} TPS', va='center', fontsize=10)
    
    ax.set_xlabel('Throughput (Transactions per Second)', fontsize=14)
    ax.set_ylabel('Transaction Type', fontsize=14)
    ax.set_title('Throughput Comparison Across Transaction Types', fontsize=16)
    
    # Add success rate annotation
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(5, i, f'({row["Success Rate (%)"]:.1f}% success)', 
               va='center', fontsize=8, color='gray')
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Throughput plot saved to {save_path}")

def create_latency_plot(latency_data, save_path='../figures/latency.png'):
    """Create latency comparison plot"""
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    df = pd.DataFrame(latency_data)
    df = df.sort_values('Avg Latency (ms)', ascending=True)
    
    x = np.arange(len(df))
    width = 0.25
    
    bars1 = ax.barh(x - width, df['Avg Latency (ms)'], height=width, 
                   label='Average', color='#2ecc71')
    bars2 = ax.barh(x, df['Max Latency (ms)'], height=width, 
                   label='Maximum', color='#e74c3c')
    bars3 = ax.barh(x + width, df['Min Latency (ms)'], height=width, 
                   label='Minimum', color='#3498db')
    
    ax.set_yticks(x)
    ax.set_yticklabels(df['Transaction Type'])
    ax.set_xlabel('Latency (ms)', fontsize=14)
    ax.set_ylabel('Transaction Type', fontsize=14)
    ax.set_title('Latency Comparison Across Transaction Types', fontsize=16)
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Latency plot saved to {save_path}")

def create_cpu_plot(cpu_data, save_path='../figures/cpu_usage.png'):
    """Create CPU usage comparison plot across Fabric versions"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    df = pd.DataFrame(cpu_data)
    
    x = np.arange(len(df))
    width = 0.25
    
    bars1 = ax.bar(x - width, df['Low Load'], width, 
                  label='Low Load', color='#2ecc71')
    bars2 = ax.bar(x, df['Medium Load'], width, 
                  label='Medium Load', color='#f39c12')
    bars3 = ax.bar(x + width, df['High Load'], width, 
                  label='High Load', color='#e74c3c')
    
    ax.set_xlabel('Hyperledger Fabric Version', fontsize=14)
    ax.set_ylabel('CPU Usage (%)', fontsize=14)
    ax.set_title('CPU Usage Comparison Across Hyperledger Fabric Versions', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(df['Version'])
    ax.legend()
    ax.set_ylim(0, 100)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.0f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"CPU usage plot saved to {save_path}")

def create_workload_scaling_plot(save_path='../figures/workload_scaling.png'):
    """Create workload scaling plot showing TPS vs transaction volume"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Simulated scaling data
    volumes = [100, 500, 1000, 1500, 2000, 2500, 3000]
    
    # Throughput scaling
    tps_submit = [153, 145, 138, 132, 125, 118, 95]
    tps_retrieve = [251, 235, 225, 215, 205, 195, 145]
    tps_update = [129, 120, 115, 108, 102, 96, 66]
    
    ax1.plot(volumes, tps_submit, 'o-', label='Add Evidence', linewidth=2, markersize=8)
    ax1.plot(volumes, tps_retrieve, 's-', label='Retrieve Evidence', linewidth=2, markersize=8)
    ax1.plot(volumes, tps_update, '^-', label='Update Evidence', linewidth=2, markersize=8)
    
    ax1.set_xlabel('Transaction Volume', fontsize=12)
    ax1.set_ylabel('Throughput (TPS)', fontsize=12)
    ax1.set_title('Throughput Scaling with Transaction Volume', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Latency scaling
    lat_submit = [202, 260, 310, 360, 410, 460, 436]
    lat_retrieve = [134, 180, 215, 245, 275, 305, 284]
    lat_update = [235, 290, 340, 395, 445, 495, 509]
    
    ax2.plot(volumes, lat_submit, 'o-', label='Add Evidence', linewidth=2, markersize=8)
    ax2.plot(volumes, lat_retrieve, 's-', label='Retrieve Evidence', linewidth=2, markersize=8)
    ax2.plot(volumes, lat_update, '^-', label='Update Evidence', linewidth=2, markersize=8)
    
    ax2.set_xlabel('Transaction Volume', fontsize=12)
    ax2.set_ylabel('Average Latency (ms)', fontsize=12)
    ax2.set_title('Latency Scaling with Transaction Volume', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Workload scaling plot saved to {save_path}")

def create_security_analysis_table(save_path='../figures/security_analysis.tex'):
    """Create LaTeX table for security analysis"""
    
    table = r"""\begin{table}[h]
\centering
\caption{Theoretical Design-Level Analysis of Attacks and Countermeasures.}
\label{tab:security_analysis}
\begin{tabular}{|p{3cm}|p{6cm}|p{5cm}|}
\hline
\textbf{Attack} & \textbf{Reason for Attack} & \textbf{Countermeasure} \\
\hline
Sybil Attack & Malicious actors create multiple fake identities to gain undue influence over the network's consensus. & Hybrid consensus using PoS+PBFT, reinforced by PKI-based identity verification and stake-weighted node selection to limit fraudulent identities. \\
\hline
DDoS Attack & Overwhelming the network with excessive traffic to cause service disruption. & Implementation of rate limiting, firewall configurations, and redundant network paths to mitigate service overload. \\
\hline
Replay Attack & Resending valid transactions to deceive the system and potentially double-spend or alter data. & Incorporation of timestamps, nonces, and smart contract validations to detect and prevent replays. \\
\hline
51\% Attack & A coalition of malicious nodes gains majority control over the network's computing power or stake. & Utilizing a permissioned blockchain combined with a hybrid PoS+PBFT consensus to restrict majority control by any single group. \\
\hline
Data Tampering Attack & Unauthorized modification of data during transmission or storage undermines integrity. & Cryptographic hashing (SHA-256) to verify data integrity, with hashes stored on an immutable blockchain and actual data preserved on IPFS. \\
\hline
Unauthorized Access & Intruders accessing sensitive data without proper clearance or credentials. & Robust Role-Based Access Control (RBAC) enforced by smart contracts, coupled with PKI authentication and digital signatures. \\
\hline
Man-in-the-Middle Attack & Interception and potential alteration of data during transmission between devices and gateways. & End-to-end encryption using TLS 1.3 and secure protocols (MQTT/CoAP) to protect data during transit. \\
\hline
IoT Device Compromise & Exploiting vulnerabilities in IoT devices, such as weak firmware or physical tampering, to gain unauthorized access. & Secure boot processes, routine firmware updates, and PKI-based device authentication to safeguard IoT devices. \\
\hline
Smart Contract Exploits & Vulnerabilities in smart contract code that can be manipulated to alter transaction outcomes. & Rigorous code audits, formal verification techniques, and multi-signature endorsement policies to secure smart contracts. \\
\hline
\end{tabular}
\end{table}"""
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w') as f:
        f.write(table)
    
    print(f"Security analysis table saved to {save_path}")

def main():
    """Main function to generate all visualizations"""
    
    # Load data
    tps_data, latency_data, cpu_data = load_simulated_data()
    
    # Create figures directory
    os.makedirs('../figures', exist_ok=True)
    
    # Generate plots
    create_throughput_plot(tps_data)
    create_latency_plot(latency_data)
    create_cpu_plot(cpu_data)
    create_workload_scaling_plot()
    create_security_analysis_table()
    
    print("\nAll visualizations generated successfully!")
    print("Figures saved to '../figures/' directory")

if __name__ == "__main__":
    main()