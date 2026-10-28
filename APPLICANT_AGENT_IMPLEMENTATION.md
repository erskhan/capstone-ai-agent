# Applicant Profile Agent Implementation

## Overview

The Applicant Profile Agent is a sophisticated multi-stage analysis system that evaluates loan applicants by validating their data, calculating risk metrics, and generating AI-powered reasoning using Claude 3.5 Sonnet. It forms the first critical stage in the loan approval workflow.

## Architecture

### File Location
- **Implementation**: `/agents/applicant_agent.py`
- **Tests**: `/tests/test_applicant_agent.py`
- **Import**: `from agents.applicant_agent import ApplicantProfileAgent`

### Core Components

#### 1. ApplicantProfileAgent Class
The main agent that orchestrates the entire applicant profile analysis workflow.

**Initialization:**
```python
from agents.applicant_agent import ApplicantProfileAgent

agent = ApplicantProfileAgent()
```

The agent automatically:
- Loads the Anthropic API key from environment configuration
- Initializes Claude 3.5 Sonnet via langchain_anthropic
- Sets timeout based on application configuration
- Configures structured logging

#### 2. Data Enums
- **IncomeStabilityLevel**: very_low, low, moderate, high, very_high
- **EmploymentRiskLevel**: very_low, low, moderate, high, very_high
- **ApplicantProfileResult**: Dataclass containing all analysis results

## Analysis Workflow

### Step 1: Data Completeness Validation
**Method**: `_validate_data_completeness(applicant, employment, credit)`

Validates all required fields across three input types:
- **Applicant Profile**: 10 fields (name, contact, SSN, address)
- **Employment Info**: 5 fields (type, employer, position, tenure, income)
- **Credit Record**: 6 fields (score, history, accounts, delinquencies, records, debt)

**Returns**:
- `validation_status`: "valid" (≥80%), "incomplete" (60-80%), "invalid" (<60% or >5 issues)
- `completeness_percentage`: Float 0-100
- `issues`: List of missing/invalid fields
- `fields_checked`: Total fields evaluated
- `fields_valid`: Valid fields found

### Step 2: Income Stability Score Calculation
**Method**: `_calculate_income_stability_score(employment, credit)`

Evaluates income reliability using four weighted factors:

| Factor | Max Points | Criteria |
|--------|------------|----------|
| Employment Duration | 30 | 5+ years (30), 2-5 years (20), 1-2 years (10), <1 year (0) |
| Employment Type | 25 | Full-time (25), Retired (20), Self-employed (15), Part-time (10), Student/Unemployed (0) |
| Credit History Length | 25 | 10+ years (25), 5-10 years (15), 2-5 years (10), <2 years (5) |
| Account Management | 20 | No delinquencies (20), 1-2 delinquencies (10), 3+ (0) |
| **Total** | **100** | **Combined Score** |

**Score Levels**:
- Very High: ≥90
- High: 75-89
- Moderate: 50-74
- Low: 25-49
- Very Low: <25

**Returns**:
```python
{
    "score": float (0-100),
    "level": IncomeStabilityLevel,
    "components": [
        {
            "factor": str,
            "score": int,
            "max_points": int,
            ...
        }
    ]
}
```

### Step 3: Employment Risk Assessment
**Method**: `_assess_employment_risk(employment, credit)`

Calculates employment-related risk factors:

| Risk Factor | Max Points | Assessment |
|------------|------------|------------|
| Employment Type Risk | 25 | Unemployed (25), Student (20), Self-employed (15), Part-time (10), Retired (5), Full-time (0) |
| Job Stability | 25 | <6 months (25), 6-12 months (15), 1-2 years (10), 2+ years (0) |
| Debt-to-Income Ratio | 25 | >50% (25), >35% (15), >25% (5), ≤25% (0) |
| Recent Delinquencies | 25 | 3+ (25), 2 (15), 1 (5), None (0) |
| **Total** | **100** | **Combined Risk Score** |

**Risk Levels**:
- Very High: ≥75
- High: 60-74
- Moderate: 40-59
- Low: 20-39
- Very Low: <20

**Returns**:
```python
{
    "score": float (0-100),
    "level": EmploymentRiskLevel,
    "risk_factors": [str],
    "debt_to_income_ratio": float
}
```

### Step 4: Credit History Summarization
**Method**: `_summarize_credit_history(credit)`

Analyzes credit profile comprehensively:

**Credit Score Categories**:
- Excellent: 750+ (Very Low Risk)
- Good: 700-749 (Low Risk)
- Fair: 650-699 (Moderate Risk)
- Poor: 600-649 (High Risk)
- Very Poor: <600 (Very High Risk)

**Account Health Assessment**:
- Healthy: No delinquencies
- At Risk: 1+ delinquencies
- Compromised: Public records present

**Returns**:
```python
{
    "score": int,
    "score_category": str,
    "score_risk_level": str,
    "years_of_history": float,
    "number_of_accounts": int,
    "current_debt": float,
    "recent_delinquencies": int,
    "public_records": int,
    "account_health": str
}
```

### Step 5: Data Anomaly Detection
**Method**: `_check_data_anomalies(applicant, employment, credit)`

Identifies inconsistencies and red flags:

1. **Age Anomalies**
   - Age < 18 years
   - Age > 120 years
   - Invalid date format

2. **Employment Anomalies**
   - Employment duration > 70 years
   - Unusually high income for employment type

3. **Credit Anomalies**
   - High credit score with recent delinquencies
   - Credit history but no accounts
   - Public records with high score
   - Debt reported but no accounts

4. **Income Anomalies**
   - >5% variance between monthly and annual income calculations

**Returns**: List of anomaly descriptions

### Step 6: AI-Powered Reasoning with Claude
**Method**: `_get_ai_reasoning(applicant, employment, credit, income_stability, employment_risk, anomalies)`

Leverages Claude 3.5 Sonnet for complex qualitative analysis:

**Input Context**:
- Full applicant profile
- Employment details with tenure
- Credit history and scores
- Calculated stability/risk scores
- Detected anomalies

**Claude Analysis Focus**:
- Income stability and reliability
- Employment risk factors
- Credit history patterns
- Overall financial health
- Red flags and concerns

**Returns**: 2-3 sentence professional assessment

## Result Structure

The `analyze()` method returns a comprehensive dictionary:

```python
{
    # Validation Status
    "validation_status": str,  # "valid", "incomplete", "invalid"
    "profile_completeness": float,  # 0-100 percentage

    # Income Stability
    "income_stability_score": float,  # 0-100
    "income_stability_level": str,  # "very_low", "low", etc.

    # Employment Risk
    "employment_risk_score": float,  # 0-100
    "employment_risk_level": str,  # "very_low", "low", etc.

    # Credit Analysis
    "credit_summary": {
        "score": int,
        "score_category": str,
        "score_risk_level": str,
        "years_of_history": float,
        "number_of_accounts": int,
        "current_debt": float,
        "recent_delinquencies": int,
        "public_records": int,
        "account_health": str
    },

    # Anomalies and Flags
    "anomalies": [str],  # List of detected issues
    "critical_issues": [str],  # Blocking issues
    "warnings": [str],  # Non-blocking concerns

    # AI Reasoning
    "reasoning": str,  # Claude's assessment

    # Timestamp
    "analyzed_at": str  # ISO format datetime
}
```

## Usage Example

```python
from agents.applicant_agent import ApplicantProfileAgent
from models.schemas import (
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    EmploymentType,
)

# Initialize agent
agent = ApplicantProfileAgent()

# Create applicant data
applicant = ApplicantProfile(
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    phone="555-1234",
    date_of_birth="1985-03-15",
    ssn="123-45-6789",
    address="123 Main St",
    city="Springfield",
    state="IL",
    zip_code="62701"
)

employment = EmploymentInfo(
    employment_type=EmploymentType.FULL_TIME,
    employer_name="Tech Corp",
    job_title="Software Engineer",
    years_employed=5.5,
    annual_income=120000.0,
    monthly_income=10000.0
)

credit = CreditRecord(
    credit_score=750,
    years_of_credit_history=10.0,
    number_of_accounts=5,
    delinquencies_last_24_months=0,
    public_records=0,
    current_debt=15000.0
)

# Analyze applicant
result = agent.analyze(applicant, employment, credit)

print(f"Status: {result['validation_status']}")
print(f"Income Stability: {result['income_stability_score']:.0f}/100")
print(f"Employment Risk: {result['employment_risk_score']:.0f}/100")
print(f"Reasoning: {result['reasoning']}")
```

## Error Handling

### Exception Types

The agent raises `AgentException` in the following scenarios:

1. **Missing API Key**
   - Anthropic API key not configured
   - Message: "ANTHROPIC_API_KEY not configured"

2. **Validation Errors**
   - Invalid input data
   - Message: "Validation failed: {details}"

3. **AI API Errors**
   - Claude API failures gracefully degrade with fallback reasoning
   - Logged as warning, not critical

### Logging

All operations are logged with structured JSON formatting:

```python
from shared.logger import get_logger
logger = get_logger("applicant_agent")

# Logs include:
# - Analysis start/completion
# - Validation status
# - Score calculations
# - Anomalies detected
# - AI reasoning details
# - Error tracebacks
```

## Environment Configuration

Required environment variables (via `.env` or system):

```env
ANTHROPIC_API_KEY=your-api-key
AGENT_TIMEOUT_SECONDS=30
LOG_LEVEL=INFO
```

## Dependencies

Added to `pyproject.toml`:
```toml
langchain-anthropic = "^0.1.0"
```

Existing dependencies used:
- langchain
- pydantic
- pydantic-settings
- anthropic

## Testing

Comprehensive test suite in `tests/test_applicant_agent.py`:

**Test Coverage**:
- Agent initialization (with and without API key)
- Data completeness validation
- Income stability score calculation
- Employment risk assessment
- Credit history summarization
- Anomaly detection
- AI reasoning fallback
- Full workflow analysis (valid and risky applicants)

**Run Tests**:
```bash
pytest tests/test_applicant_agent.py -v
pytest tests/test_applicant_agent.py --cov=agents.applicant_agent
```

## Integration with Orchestrator

The agent is registered with the LoanApprovalOrchestrator:

```python
from agents import ApplicantProfileAgent
from agents.orchestrator import LoanApprovalOrchestrator

orchestrator = LoanApprovalOrchestrator()
applicant_agent = ApplicantProfileAgent()
orchestrator.register_agent("applicant_profile", applicant_agent)
```

## Scoring Methodology

### Income Stability (0-100)
Weighted assessment of employment permanence and consistency:
- Long employment duration (5+ years) = highly stable
- Established credit history (10+ years) = proven reliability
- No recent delinquencies = consistent payment behavior
- Full-time employment = stable income source

### Employment Risk (0-100)
Inverse assessment of employment-related vulnerability:
- Recent job changes = higher risk
- Self-employment or part-time = moderate risk
- High debt-to-income ratio = higher risk
- Recent delinquencies = higher risk

## Future Enhancements

Potential additions to the agent:

1. **Multi-source Verification**
   - Integrate with credit bureaus
   - Employment verification APIs
   - Income documentation analysis

2. **Advanced Analytics**
   - Probability of default (PD) calculation
   - Income volatility analysis
   - Cash flow forecasting

3. **Machine Learning Integration**
   - Historical outcome prediction
   - Dynamic score calibration
   - Pattern recognition for fraud

4. **External Data Integration**
   - Economic indicators
   - Industry-specific risk factors
   - Macroeconomic influences

## Compliance & Audit

- All analysis results logged with timestamps
- Full reasoning trail captured for compliance
- Audit trail integration ready
- Fair lending compliance in score calculations
- Data protection following GDPR/CCPA standards
