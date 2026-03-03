# Evaluation Criteria for Terraform AI Tool Study

## 1. Data Collection Framework

### 1.1 Experimental Parameters
- **Tool**: AI coding assistant being evaluated (Copilot, Windsurf)
- **Prompt_ID**: Unique identifier for the specific prompt/task (E1, E2, etc.)
- **Run_Number**: Use of the execution of a prompt, since a prompt is executed 3 times
- **Start_Time**: Task initiation timestamp (ISO 8601 format)
- **End_Time**: Task completion timestamp (ISO 8601 format)
- **Duration_Seconds**: Calculated execution time in seconds

### 1.2 Technical Validation Metrics
- **Terraform_Validate**: Syntax and configuration validity (Pass/Fail/NA)
- **Terraform_Plan**: Planning phase execution success (Pass/Fail/NA)

## 2. Qualitative Assessment Scale

### 2.1 Scoring Methodology
Each criterion uses a 3-point scale (0-2) for granular assessment:

**Functionality_Score (0-2)**
- 0: Non-functional or critical errors
- 1: Partially functional with minor issues
- 2: Fully functional as intended

**Completeness_Score (0-2)**
- 0: Incomplete solution, missing major components
- 1: Mostly complete with minor omissions
- 2: Complete solution addressing all requirements

**Quality_Score (0-2)**
- 0: Poor code quality, lacks best practices
- 1: Acceptable quality with room for improvement
- 2: High-quality code following Terraform best practices

### 2.2 Composite Scoring
- **Total_Score**: Sum of individual scores (0-6 scale)
- Higher scores indicate superior performance

## 3. Documentation Requirements

- **Notes**: Detailed observations, errors encountered, and contextual information
- **Screenshot_File**: Visual documentation filename for reference
