import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set publication-ready style
plt.style.use('default')
sns.set_palette("deep")
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.titlesize': 18,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3
})

class TerraformAIAnalyzer:
    def __init__(self, data_path):
        self.data_path = Path(data_path)
        self.output_dir = self.data_path.parent / "results"
        self.output_dir.mkdir(exist_ok=True)
        self.df = None
        
    def load_and_clean_data(self):
        """Load and clean the Excel data"""
        print("Loading Terraform AI Study data...")
        
        # Read Excel with proper header detection
        raw_df = pd.read_excel(self.data_path, header=None)
        
        # Find header row
        header_row = None
        for i in range(min(10, len(raw_df))):
            row_values = raw_df.iloc[i].astype(str).tolist()
            if any('tool' in str(val).lower() for val in row_values):
                header_row = i
                break
        
        if header_row is not None:
            self.df = pd.read_excel(self.data_path, header=header_row)
        else:
            self.df = pd.read_excel(self.data_path, header=2)
        
        # Clean column names
        self.df.columns = [str(col).strip() for col in self.df.columns]
        
        # Remove empty rows
        self.df = self.df.dropna(how='all')
        
        # Data type conversions
        bool_mappings = {
            'Pass': True, 'Fail': False, 'NA': None,
            'Success': True, 'Fail': False, 'NA': None
        }
        
        validate_cols = ['Terraform_Validate (Pass/Fail/NA)', 'Terraform_Plan (Pass/Fail/NA)']
        apply_cols = ['Code_Apply (Success/Fail/NA)']
        
        for col in validate_cols + apply_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].map(bool_mappings)
        
        # Extract difficulty from Prompt_ID
        if 'Prompt_ID' in self.df.columns:
            self.df['Difficulty'] = self.df['Prompt_ID'].str[0]
            self.df['Difficulty_Full'] = self.df['Difficulty'].map({
                'E': 'Easy', 'M': 'Medium', 'C': 'Complex'
            })
        
        # Parse timestamps
        time_cols = ['Start_Time', 'End_Time']
        for col in time_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col])
        
        print(f"Data loaded: {len(self.df)} records")
        print(f"Tools: {self.df['Tool'].unique()}")
        print(f"Prompts: {sorted(self.df['Prompt_ID'].unique())}")
        
        return self.df
    
    def calculate_comprehensive_statistics(self):
        """Calculate all statistical measures"""
        print("\n" + "="*70)
        print("COMPREHENSIVE STATISTICAL ANALYSIS")
        print("="*70)
        
        stats_results = {}
        tools = self.df['Tool'].unique()
        
        # Overall Performance Metrics
        print("\n1. OVERALL PERFORMANCE METRICS")
        print("-" * 40)
        
        for tool in tools:
            tool_data = self.df[self.df['Tool'] == tool]
            
            # Success rates
            validate_success = tool_data['Terraform_Validate (Pass/Fail/NA)'].mean() * 100
            plan_success = tool_data['Terraform_Plan (Pass/Fail/NA)'].mean() * 100
            
            # Score metrics
            mean_total = tool_data['Total_Score (0-6)'].mean()
            std_total = tool_data['Total_Score (0-6)'].std()
            mean_func = tool_data['Functionality_Score (0-2)'].mean()
            mean_comp = tool_data['Completeness_Score (0-2)'].mean()
            mean_qual = tool_data['Quality_Score (0-2)'].mean()
            
            # Duration
            mean_duration = tool_data['Duration_Seconds'].mean()
            
            stats_results[tool] = {
                'validate_success': validate_success,
                'plan_success': plan_success,
                'mean_total_score': mean_total,
                'std_total_score': std_total,
                'mean_functionality': mean_func,
                'mean_completeness': mean_comp,
                'mean_quality': mean_qual,
                'mean_duration': mean_duration
            }
            
            print(f"\n{tool}:")
            print(f"  Terraform Validate Success: {validate_success:.1f}%")
            print(f"  Terraform Plan Success: {plan_success:.1f}%")
            print(f"  Total Score: {mean_total:.2f} ± {std_total:.2f}")
            print(f"  Functionality: {mean_func:.2f}/2.0")
            print(f"  Completeness: {mean_comp:.2f}/2.0")
            print(f"  Quality: {mean_qual:.2f}/2.0")
            print(f"  Avg Duration: {mean_duration:.1f}s")
        
        # Statistical significance tests
        print(f"\n2. STATISTICAL SIGNIFICANCE TESTS")
        print("-" * 40)
        
        if len(tools) == 2:
            tool1_data = self.df[self.df['Tool'] == tools[0]]['Total_Score (0-6)']
            tool2_data = self.df[self.df['Tool'] == tools[1]]['Total_Score (0-6)']
            
            t_stat, p_value = stats.ttest_ind(tool1_data, tool2_data)
            print(f"T-test for Total Scores:")
            print(f"  t-statistic: {t_stat:.3f}")
            print(f"  p-value: {p_value:.4f}")
            print(f"  Significant difference: {'Yes' if p_value < 0.05 else 'No'} (α=0.05)")
        
        # Performance by Difficulty
        print(f"\n3. PERFORMANCE BY DIFFICULTY LEVEL")
        print("-" * 40)
        
        for difficulty in ['Easy', 'Medium', 'Complex']:
            print(f"\n{difficulty} Tasks:")
            diff_data = self.df[self.df['Difficulty_Full'] == difficulty]
            
            for tool in tools:
                tool_diff_data = diff_data[diff_data['Tool'] == tool]
                if len(tool_diff_data) > 0:
                    validate_rate = tool_diff_data['Terraform_Validate (Pass/Fail/NA)'].mean() * 100
                    plan_rate = tool_diff_data['Terraform_Plan (Pass/Fail/NA)'].mean() * 100
                    avg_score = tool_diff_data['Total_Score (0-6)'].mean()
                    
                    print(f"  {tool}: Validate {validate_rate:.0f}%, Plan {plan_rate:.0f}%, Score {avg_score:.1f}")
        
        return stats_results
    
    def create_success_rates_chart(self):
        """Create Terraform command success rates chart"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        tools = self.df['Tool'].unique()
        colors = ['#2E8B57', '#DC143C']
        
        validate_rates = []
        plan_rates = []
        
        for tool in tools:
            tool_data = self.df[self.df['Tool'] == tool]
            validate_rates.append(tool_data['Terraform_Validate (Pass/Fail/NA)'].mean() * 100)
            plan_rates.append(tool_data['Terraform_Plan (Pass/Fail/NA)'].mean() * 100)
        
        x = np.arange(len(tools))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, validate_rates, width, label='Terraform Validate', color=colors[0], alpha=0.8)
        bars2 = ax.bar(x + width/2, plan_rates, width, label='Terraform Plan', color=colors[1], alpha=0.8)
        
        ax.set_title('Terraform Command Success Rates', fontsize=16, fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontsize=14)
        ax.set_xlabel('AI Coding Assistant', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(tools)
        ax.legend()
        ax.set_ylim(0, 105)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '1_success_rates.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_score_distribution_chart(self):
        """Create total score distribution chart"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        tools = self.df['Tool'].unique()
        colors = ['#2E8B57', '#DC143C']
        
        score_data = []
        for tool in tools:
            tool_data = self.df[self.df['Tool'] == tool]
            scores = tool_data['Total_Score (0-6)'].tolist()
            score_data.extend([(tool, score) for score in scores])
        
        score_df = pd.DataFrame(score_data, columns=['Tool', 'Total_Score'])
        sns.boxplot(data=score_df, x='Tool', y='Total_Score', ax=ax, palette=colors)
        ax.set_title('Total Score Distribution', fontsize=16, fontweight='bold')
        ax.set_ylabel('Total Score (0-6)', fontsize=14)
        ax.set_xlabel('AI Coding Assistant', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '2_score_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_difficulty_performance_chart(self):
        """Create performance by difficulty chart"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        tools = self.df['Tool'].unique()
        colors = ['#2E8B57', '#DC143C']
        
        difficulty_data = []
        for difficulty in ['Easy', 'Medium', 'Complex']:
            for tool in tools:
                tool_diff = self.df[(self.df['Tool'] == tool) & (self.df['Difficulty_Full'] == difficulty)]
                avg_score = tool_diff['Total_Score (0-6)'].mean()
                difficulty_data.append({'Difficulty': difficulty, 'Tool': tool, 'Score': avg_score})
        
        diff_df = pd.DataFrame(difficulty_data)
        sns.barplot(data=diff_df, x='Difficulty', y='Score', hue='Tool', ax=ax, palette=colors)
        ax.set_title('Performance by Task Difficulty', fontsize=16, fontweight='bold')
        ax.set_ylabel('Average Total Score', fontsize=14)
        ax.set_xlabel('Task Difficulty', fontsize=14)
        ax.legend(title='AI Coding Assistant')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '3_difficulty_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_duration_comparison_chart(self):
        """Create duration comparison chart"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        tools = self.df['Tool'].unique()
        colors = ['#2E8B57', '#DC143C']
        
        duration_data = []
        for tool in tools:
            tool_data = self.df[self.df['Tool'] == tool]
            durations = tool_data['Duration_Seconds'].tolist()
            duration_data.extend([(tool, duration) for duration in durations])
        
        dur_df = pd.DataFrame(duration_data, columns=['Tool', 'Duration'])
        sns.boxplot(data=dur_df, x='Tool', y='Duration', ax=ax, palette=colors)
        ax.set_title('Task Completion Time Comparison', fontsize=16, fontweight='bold')
        ax.set_ylabel('Duration (seconds)', fontsize=14)
        ax.set_xlabel('AI Coding Assistant', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '4_duration_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_score_components_chart(self):
        """Create score components comparison chart"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        tools = self.df['Tool'].unique()
        colors = ['#2E8B57', '#DC143C']
        
        score_components = ['Functionality_Score (0-2)', 'Completeness_Score (0-2)', 'Quality_Score (0-2)']
        component_names = ['Functionality', 'Completeness', 'Quality']
        
        comp_data = []
        for tool in tools:
            tool_data = self.df[self.df['Tool'] == tool]
            for comp, name in zip(score_components, component_names):
                avg_score = tool_data[comp].mean()
                comp_data.append({'Component': name, 'Tool': tool, 'Score': avg_score})
        
        comp_df = pd.DataFrame(comp_data)
        sns.barplot(data=comp_df, x='Component', y='Score', hue='Tool', ax=ax, palette=colors)
        ax.set_title('Score Components Comparison', fontsize=16, fontweight='bold')
        ax.set_ylabel('Average Score', fontsize=14)
        ax.set_xlabel('Score Component', fontsize=14)
        ax.set_ylim(0, 2.1)
        ax.legend(title='AI Coding Assistant')
        
        # Add value labels
        for container in ax.containers:
            ax.bar_label(container, fmt='%.2f', padding=3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '5_score_components.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_performance_heatmap_chart(self):
        """Create performance heatmap by prompt"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        tools = self.df['Tool'].unique()
        
        heatmap_data = []
        for tool in tools:
            for prompt in sorted(self.df['Prompt_ID'].unique()):
                tool_prompt_data = self.df[(self.df['Tool'] == tool) & (self.df['Prompt_ID'] == prompt)]
                avg_score = tool_prompt_data['Total_Score (0-6)'].mean()
                heatmap_data.append({'Tool': tool, 'Prompt': prompt, 'Score': avg_score})
        
        heat_df = pd.DataFrame(heatmap_data)
        pivot_heat = heat_df.pivot(index='Prompt', columns='Tool', values='Score')
        
        sns.heatmap(pivot_heat, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax,
                   cbar_kws={'label': 'Average Score'})
        ax.set_title('Performance Heatmap by Prompt', fontsize=16, fontweight='bold')
        ax.set_ylabel('Terraform Prompt', fontsize=14)
        ax.set_xlabel('AI Coding Assistant', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '6_performance_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_success_by_difficulty_chart(self):
        """Create success rates by difficulty chart"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        tools = self.df['Tool'].unique()
        colors = ['#2E8B57', '#DC143C']
        
        success_data = []
        for difficulty in ['Easy', 'Medium', 'Complex']:
            for tool in tools:
                tool_diff = self.df[(self.df['Tool'] == tool) & (self.df['Difficulty_Full'] == difficulty)]
                validate_rate = tool_diff['Terraform_Validate (Pass/Fail/NA)'].mean() * 100
                plan_rate = tool_diff['Terraform_Plan (Pass/Fail/NA)'].mean() * 100
                
                success_data.append({'Difficulty': difficulty, 'Tool': tool, 
                                   'Validate': validate_rate, 'Plan': plan_rate})
        
        success_df = pd.DataFrame(success_data)
        
        x = np.arange(len(['Easy', 'Medium', 'Complex']))
        width = 0.15
        
        for i, tool in enumerate(tools):
            tool_data = success_df[success_df['Tool'] == tool]
            ax.bar(x + i*width*2 - width/2, tool_data['Validate'], width, 
                   label=f'{tool} - Validate', color=colors[i], alpha=0.8)
            ax.bar(x + i*width*2 + width/2, tool_data['Plan'], width,
                   label=f'{tool} - Plan', color=colors[i], alpha=0.5)
        
        ax.set_title('Success Rates by Task Difficulty', fontsize=16, fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontsize=14)
        ax.set_xlabel('Task Difficulty', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(['Easy', 'Medium', 'Complex'])
        ax.legend()
        ax.set_ylim(0, 105)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '7_success_by_difficulty.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_correlation_heatmap_chart(self):
        """Create score component correlations chart"""
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
        corr_data = self.df[['Functionality_Score (0-2)', 'Completeness_Score (0-2)', 
                            'Quality_Score (0-2)', 'Duration_Seconds']].corr()
        
        sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax)
        ax.set_title('Score Component Correlations', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '8_correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_comprehensive_report(self, stats_results):
        """Generate comprehensive markdown report"""
        report_path = self.output_dir / 'comprehensive_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Terraform AI Coding Assistants: Comprehensive Analysis Report\n\n")
            
            f.write("## Executive Summary\n\n")
            f.write("This report presents a comprehensive evaluation of two AI coding assistants ")
            f.write("(GitHub Copilot and Windsurf Cascade) in the context of Terraform ")
            f.write("Infrastructure as Code development.\n\n")
            
            f.write("### Study Design\n")
            f.write(f"- **Tools Evaluated**: {', '.join(self.df['Tool'].unique())}\n")
            f.write(f"- **Total Prompts**: 11 (Easy: 3, Medium: 4, Complex: 4)\n")
            f.write(f"- **Runs per Tool per Prompt**: 3\n")
            f.write(f"- **Total Evaluations**: {len(self.df)} data points\n")
            f.write(f"- **Evaluation Metrics**: Terraform validation, planning success, ")
            f.write("functionality, completeness, quality scores\n\n")
            
            # Detailed Results
            f.write("## Detailed Results\n\n")
            
            f.write("### 1. Overall Performance Comparison\n\n")
            f.write("| Metric | Windsurf | VSCode - Copilot |\n")
            f.write("|--------|----------|-------------------|\n")
            
            tools = list(stats_results.keys())
            if len(tools) >= 2:
                windsurf_key = next(k for k in tools if 'Windsurf' in k)
                copilot_key = next(k for k in tools if 'Copilot' in k)
                
                f.write(f"| Terraform Validate Success | {stats_results[windsurf_key]['validate_success']:.1f}% | {stats_results[copilot_key]['validate_success']:.1f}% |\n")
                f.write(f"| Terraform Plan Success | {stats_results[windsurf_key]['plan_success']:.1f}% | {stats_results[copilot_key]['plan_success']:.1f}% |\n")
                f.write(f"| Total Score (0-6) | {stats_results[windsurf_key]['mean_total_score']:.2f} ± {stats_results[windsurf_key]['std_total_score']:.2f} | {stats_results[copilot_key]['mean_total_score']:.2f} ± {stats_results[copilot_key]['std_total_score']:.2f} |\n")
                f.write(f"| Functionality Score | {stats_results[windsurf_key]['mean_functionality']:.2f}/2.0 | {stats_results[copilot_key]['mean_functionality']:.2f}/2.0 |\n")
                f.write(f"| Completeness Score | {stats_results[windsurf_key]['mean_completeness']:.2f}/2.0 | {stats_results[copilot_key]['mean_completeness']:.2f}/2.0 |\n")
                f.write(f"| Quality Score | {stats_results[windsurf_key]['mean_quality']:.2f}/2.0 | {stats_results[copilot_key]['mean_quality']:.2f}/2.0 |\n")
                f.write(f"| Average Duration | {stats_results[windsurf_key]['mean_duration']:.1f}s | {stats_results[copilot_key]['mean_duration']:.1f}s |\n\n")
            
            f.write("### 2. Performance by Task Difficulty\n\n")
            for difficulty in ['Easy', 'Medium', 'Complex']:
                f.write(f"#### {difficulty} Tasks\n\n")
                diff_data = self.df[self.df['Difficulty_Full'] == difficulty]
                
                f.write("| Tool | Validate Success | Plan Success | Avg Score |\n")
                f.write("|------|-----------------|--------------|----------|\n")
                
                for tool in self.df['Tool'].unique():
                    tool_diff_data = diff_data[diff_data['Tool'] == tool]
                    if len(tool_diff_data) > 0:
                        validate_rate = tool_diff_data['Terraform_Validate (Pass/Fail/NA)'].mean() * 100
                        plan_rate = tool_diff_data['Terraform_Plan (Pass/Fail/NA)'].mean() * 100
                        avg_score = tool_diff_data['Total_Score (0-6)'].mean()
                        
                        f.write(f"| {tool} | {validate_rate:.0f}% | {plan_rate:.0f}% | {avg_score:.2f} |\n")
                
                f.write("\n")
            
            f.write("## Key Findings\n\n")
            
            # Determine winner for each category
            if len(tools) >= 2:
                windsurf_total = stats_results[windsurf_key]['mean_total_score']
                copilot_total = stats_results[copilot_key]['mean_total_score']
                
                f.write(f"1. **Overall Performance**: ")
                f.write(f"{'Windsurf' if windsurf_total > copilot_total else 'Copilot'} ")
                f.write(f"achieved higher overall scores ({max(windsurf_total, copilot_total):.2f} vs {min(windsurf_total, copilot_total):.2f})\n\n")
                
                windsurf_validate = stats_results[windsurf_key]['validate_success']
                copilot_validate = stats_results[copilot_key]['validate_success']
                
                f.write(f"2. **Terraform Validation**: ")
                f.write(f"{'Windsurf' if windsurf_validate > copilot_validate else 'Copilot'} ")
                f.write(f"had higher validation success rates ({max(windsurf_validate, copilot_validate):.1f}% vs {min(windsurf_validate, copilot_validate):.1f}%)\n\n")
                
                windsurf_duration = stats_results[windsurf_key]['mean_duration']
                copilot_duration = stats_results[copilot_key]['mean_duration']
                
                f.write(f"3. **Efficiency**: ")
                f.write(f"{'Windsurf' if windsurf_duration < copilot_duration else 'Copilot'} ")
                f.write(f"was faster on average ({min(windsurf_duration, copilot_duration):.1f}s vs {max(windsurf_duration, copilot_duration):.1f}s)\n\n")
            
            f.write("## Conclusions\n\n")
            f.write("Based on this comprehensive analysis of Terraform Infrastructure as Code ")
            f.write("development with AI coding assistants, the study reveals significant ")
            f.write("performance differences between the evaluated tools across various metrics ")
            f.write("including code quality, completeness, and execution success rates.\n\n")

        
        print(f"Comprehensive report saved to: {report_path}")
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline"""
        print("Starting Comprehensive Terraform AI Analysis...")
        print("="*70)
        
        # Load and prepare data
        self.load_and_clean_data()
        
        # Calculate statistics
        stats_results = self.calculate_comprehensive_statistics()
        
        # Generate individual visualizations
        print("\nGenerating individual publication-ready charts...")
        self.create_success_rates_chart()
        self.create_score_distribution_chart()
        self.create_difficulty_performance_chart()
        self.create_duration_comparison_chart()
        self.create_score_components_chart()
        self.create_performance_heatmap_chart()
        self.create_success_by_difficulty_chart()
        self.create_correlation_heatmap_chart()
        
        # Generate comprehensive report
        self.generate_comprehensive_report(stats_results)
        
        print(f"\n{'='*70}")
        print("Analysis Complete!")
        print(f"All outputs saved to: {self.output_dir}")
        print("Individual charts generated:")
        for file in sorted(self.output_dir.glob("*.png")):
            print(f"  - {file.name}")
        print("Report generated:")
        print(f"  - comprehensive_analysis_report.md")
        print(f"{'='*70}")

if __name__ == "__main__":
    # Initialize and run analysis
    data_path = "/Users/lukasbuck/Code/research/terraform-ai-study/04-analysis/raw-data.xlsx"
    analyzer = TerraformAIAnalyzer(data_path)
    analyzer.run_complete_analysis()
