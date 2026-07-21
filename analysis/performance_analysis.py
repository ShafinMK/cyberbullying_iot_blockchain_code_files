#!/usr/bin/env python3
"""
Performance Analysis Script for Forensic Blockchain System
Analyzes throughput, latency, and resource utilization from benchmark results
Based on Section 4 of the paper
"""

import json
import csv
import os
import argparse
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class PerformanceAnalyzer:
    """Analyzes performance data from Hyperledger Caliper benchmarks"""
    
    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        self.data = {}
        self.load_data()
    
    def load_data(self):
        """Load benchmark results from JSON files"""
        
        result_files = [f for f in os.listdir(self.results_dir) if f.endswith('.json')]
        
        for file in result_files:
            filepath = os.path.join(self.results_dir, file)
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Extract key metrics
                for round_data in data.get('rounds', []):
                    label = round_data.get('label', 'unknown')
                    self.data[label] = {
                        'throughput': round_data.get('throughput', 0),
                        'latency_avg': round_data.get('latency_avg', 0),
                        'latency_max': round_data.get('latency_max', 0),
                        'latency_min': round_data.get('latency_min', 0),
                        'success_rate': round_data.get('success_rate', 0),
                        'tx_count': round_data.get('tx_count', 0),
                        'cpu_usage': round_data.get('cpu_usage', 0),
                        'memory_usage': round_data.get('memory_usage', 0)
                    }
        
        print(f"Loaded data for {len(self.data)} transaction types")
    
    def analyze_throughput(self) -> pd.DataFrame:
        """Analyze throughput across transaction types"""
        
        results = []
        for label, metrics in self.data.items():
            results.append({
                'Transaction Type': label,
                'Throughput (TPS)': metrics['throughput'],
                'Success Rate (%)': metrics['success_rate'],
                'Total Transactions': metrics['tx_count']
            })
        
        return pd.DataFrame(results)
    
    def analyze_latency(self) -> pd.DataFrame:
        """Analyze latency across transaction types"""
        
        results = []
        for label, metrics in self.data.items():
            results.append({
                'Transaction Type': label,
                'Avg Latency (ms)': metrics['latency_avg'],
                'Max Latency (ms)': metrics['latency_max'],
                'Min Latency (ms)': metrics['latency_min']
            })
        
        return pd.DataFrame(results)
    
    def analyze_resource_usage(self) -> pd.DataFrame:
        """Analyze CPU and memory usage"""
        
        results = []
        for label, metrics in self.data.items():
            results.append({
                'Transaction Type': label,
                'CPU Usage (%)': metrics.get('cpu_usage', 0),
                'Memory Usage (MB)': metrics.get('memory_usage', 0)
            })
        
        return pd.DataFrame(results)
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of all performance metrics"""
        
        report = []
        report.append("=" * 60)
        report.append("FORENSIC BLOCKCHAIN PERFORMANCE SUMMARY")
        report.append("=" * 60)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Throughput summary
        df_throughput = self.analyze_throughput()
        report.append("THROUGHPUT SUMMARY:")
        report.append("-" * 40)
        for _, row in df_throughput.iterrows():
            report.append(f"  {row['Transaction Type']:20s}: {row['Throughput (TPS)']:6.1f} TPS  ({row['Success Rate (%)']:.1f}% success)")
        report.append("")
        
        # Latency summary
        df_latency = self.analyze_latency()
        report.append("LATENCY SUMMARY:")
        report.append("-" * 40)
        for _, row in df_latency.iterrows():
            report.append(f"  {row['Transaction Type']:20s}: Avg {row['Avg Latency (ms)']:6.1f} ms  (Max {row['Max Latency (ms)']:.1f} ms)")
        report.append("")
        
        # Resource usage summary
        df_resource = self.analyze_resource_usage()
        report.append("RESOURCE USAGE SUMMARY:")
        report.append("-" * 40)
        for _, row in df_resource.iterrows():
            if row['CPU Usage (%)'] > 0:
                report.append(f"  {row['Transaction Type']:20s}: CPU {row['CPU Usage (%)']:.1f}%  Memory {row['Memory Usage (MB)']:.1f} MB")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_latex_tables(self) -> Dict[str, str]:
        """Generate LaTeX tables for the manuscript"""
        
        tables = {}
        
        # Throughput table
        df = self.analyze_throughput()
        rows = []
        for _, row in df.iterrows():
            rows.append(f"    {row['Transaction Type']} & {row['Throughput (TPS)']:.0f} & {row['Success Rate (%)']:.1f}\\% \\\\")
        tables['throughput'] = "\n".join(rows)
        
        # Latency table
        df = self.analyze_latency()
        rows = []
        for _, row in df.iterrows():
            rows.append(f"    {row['Transaction Type']} & {row['Avg Latency (ms)']:.0f} & {row['Max Latency (ms)']:.0f} & {row['Min Latency (ms)']:.0f} \\\\")
        tables['latency'] = "\n".join(rows)
        
        return tables


class Visualizer:
    """Creates visualizations for performance data"""
    
    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer
        self.setup_style()
    
    def setup_style(self):
        """Set up matplotlib style for publication-quality figures"""
        
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("Set2")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['legend.fontsize'] = 11
    
    def plot_throughput_comparison(self, save_path: str = None):
        """Plot throughput comparison across transaction types"""
        
        df = self.analyzer.analyze_throughput()
        
        fig, ax = plt.subplots()
        bars = ax.bar(df['Transaction Type'], df['Throughput (TPS)'], 
                     color=sns.color_palette("Set2", len(df)))
        
        ax.set_xlabel('Transaction Type')
        ax.set_ylabel('Throughput (Transactions per Second)')
        ax.set_title('Throughput Comparison Across Transaction Types')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{height:.0f}', ha='center', va='bottom', fontsize=10)
        
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_latency_comparison(self, save_path: str = None):
        """Plot latency comparison across transaction types"""
        
        df = self.analyzer.analyze_latency()
        
        fig, ax = plt.subplots()
        
        x = np.arange(len(df))
        width = 0.25
        
        bars1 = ax.bar(x - width, df['Avg Latency (ms)'], width, label='Average', color='#2ecc71')
        bars2 = ax.bar(x, df['Max Latency (ms)'], width, label='Maximum', color='#e74c3c')
        bars3 = ax.bar(x + width, df['Min Latency (ms)'], width, label='Minimum', color='#3498db')
        
        ax.set_xlabel('Transaction Type')
        ax.set_ylabel('Latency (ms)')
        ax.set_title('Latency Comparison Across Transaction Types')
        ax.set_xticks(x)
        ax.set_xticklabels(df['Transaction Type'], rotation=30, ha='right')
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_cpu_usage(self, save_path: str = None):
        """Plot CPU usage across Hyperledger Fabric versions"""
        
        # Simulated data (replace with actual data)
        versions = ['v2.2', 'v2.3', 'v2.4', 'v2.5']
        low_load = [28, 24, 20, 16]
        medium_load = [47, 40, 33, 27]
        high_load = [92, 78, 65, 53]
        
        fig, ax = plt.subplots()
        
        x = np.arange(len(versions))
        width = 0.25
        
        ax.bar(x - width, low_load, width, label='Low Load', color='#2ecc71')
        ax.bar(x, medium_load, width, label='Medium Load', color='#f39c12')
        ax.bar(x + width, high_load, width, label='High Load', color='#e74c3c')
        
        ax.set_xlabel('Hyperledger Fabric Version')
        ax.set_ylabel('CPU Usage (%)')
        ax.set_title('CPU Usage Comparison Across Hyperledger Fabric Versions')
        ax.set_xticks(x)
        ax.set_xticklabels(versions)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Performance Analysis for Forensic Blockchain System')
    parser.add_argument('--results-dir', default='./results', help='Directory containing benchmark results')
    parser.add_argument('--output-dir', default='./output', help='Directory for output files')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load and analyze data
    analyzer = PerformanceAnalyzer(args.results_dir)
    
    # Generate summary report
    report = analyzer.generate_summary_report()
    print(report)
    
    # Save report
    report_path = os.path.join(args.output_dir, 'performance_summary.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to {report_path}")
    
    # Generate LaTeX tables
    tables = analyzer.generate_latex_tables()
    for name, content in tables.items():
        latex_path = os.path.join(args.output_dir, f'table_{name}.tex')
        with open(latex_path, 'w') as f:
            f.write(content)
        print(f"LaTeX table saved to {latex_path}")
    
    # Generate visualizations
    if args.visualize:
        visualizer = Visualizer(analyzer)
        visualizer.plot_throughput_comparison(
            os.path.join(args.output_dir, 'throughput_comparison.png')
        )
        visualizer.plot_latency_comparison(
            os.path.join(args.output_dir, 'latency_comparison.png')
        )
        visualizer.plot_cpu_usage(
            os.path.join(args.output_dir, 'cpu_usage_comparison.png')
        )


if __name__ == "__main__":
    main()