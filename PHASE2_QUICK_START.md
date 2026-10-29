# Phase 2 Quick Start Guide

## Running Phase 2 Components

### Test the Agents Individually

```bash
# Test Applicant Profile Agent
python -c "
from models.schemas import ApplicantProfile, EmploymentInfo, CreditRecord, EmploymentType
from agents.applicant_agent import ApplicantProfileAgent

agent = ApplicantProfileAgent()
applicant = ApplicantProfile(
    first_name='John', last_name='Doe', email='john@example.com',
    phone='5551234567', date_of_birth='1985-06-15', ssn='123456789',
    address='123 Main St', city='San Francisco', state='CA', zip_code='94102'
)
employment = EmploymentInfo(
    employment_type=EmploymentType.FULL_TIME, employer_name='Tech Corp',
    job_title='Engineer', years_employed=5.5, annual_income=150000.0
)
credit = CreditRecord(credit_score=750, years_of_credit_history=12.0,
    number_of_accounts=5, delinquencies_last_24_months=0,
    public_records=0, current_debt=25000.0)

result = agent.analyze(applicant, employment, credit)
print('✅ Applicant Agent Works')
print(f'Income Stability: {result[\"income_stability_score\"]:.0f}')
print(f'Employment Risk: {result[\"employment_risk_score\"]:.0f}')
"
```

### Test the Financial Risk Agent

```bash
# Test Financial Risk Agent
python -c "
from models.schemas import *
from agents.risk_agent import FinancialRiskAnalysisAgent

agent = FinancialRiskAnalysisAgent()
app = LoanApplicationRequest(
    applicant_profile=ApplicantProfile(
        first_name='Jane', last_name='Smith', email='jane@example.com',
        phone='5559876543', date_of_birth='1988-03-20', ssn='987654321',
        address='456 Oak Ave', city='Los Angeles', state='CA', zip_code='90001'
    ),
    employment_info=EmploymentInfo(
        employment_type=EmploymentType.FULL_TIME, employer_name='TechCorp',
        job_title='Manager', years_employed=3.0, annual_income=120000.0
    ),
    credit_record=CreditRecord(credit_score=700, years_of_credit_history=8.0,
        number_of_accounts=4, delinquencies_last_24_months=0,
        public_records=0, current_debt=30000.0),
    loan_details=LoanDetails(
        loan_amount=50000.0, loan_purpose='Home Improvement',
        loan_term_months=60, interest_rate=5.5
    )
)

result = agent.analyze(app)
print('✅ Risk Agent Works')
print(f'Risk Score: {result[\"risk_score\"]:.0f}')
print(f'DTI Ratio: {result[\"dti_ratio\"]:.1f}%')
"
```

### Test the Decision Agent

```bash
# Test Decision Agent
python -c "
from models.schemas import *
from agents.applicant_agent import ApplicantProfileAgent
from agents.risk_agent import FinancialRiskAnalysisAgent
from agents.decision_agent import LoanDecisionAgent

# Create application
app = LoanApplicationRequest(
    applicant_profile=ApplicantProfile(...),  # Fill as above
    employment_info=EmploymentInfo(...),
    credit_record=CreditRecord(...),
    loan_details=LoanDetails(...)
)

# Get analyses
applicant_agent = ApplicantProfileAgent()
risk_agent = FinancialRiskAnalysisAgent()
applicant_result = applicant_agent.analyze(app.applicant_profile, app.employment_info, app.credit_record)
risk_result = risk_agent.analyze(app)

# Make decision
decision_agent = LoanDecisionAgent()
decision = decision_agent.decide(app, applicant_result, risk_result)
print('✅ Decision Agent Works')
print(f'Decision: {decision[\"classification\"]}')
print(f'Confidence: {decision[\"confidence_score\"]:.2f}')
"
```

### Run End-to-End Tests

```bash
# Run all Phase 2 tests
pytest tests/test_phase2_e2e.py -v

# Run specific test
pytest tests/test_phase2_e2e.py::TestLoanApprovalOrchestrator::test_end_to_end_good_applicant -v

# Run with output
pytest tests/test_phase2_e2e.py -v -s
```

### Test the Orchestrator

```bash
# Test orchestrator workflow
python -c "
from uuid import uuid4
from models.schemas import *
from agents.orchestrator import LoanApprovalOrchestrator

# Create sample application
app = LoanApplicationRequest(
    applicant_profile=ApplicantProfile(...),  # Fill as above
    employment_info=EmploymentInfo(...),
    credit_record=CreditRecord(...),
    loan_details=LoanDetails(...)
)

# Run orchestrator
orchestrator = LoanApprovalOrchestrator()
result = orchestrator.process_application(
    application=app,
    application_id=str(uuid4()),
    correlation_id=str(uuid4())
)

print('✅ Orchestrator Works')
print(f'Workflow State: {result[\"workflow_state\"]}')
print(f'Decision: {result[\"decision\"][\"classification\"]}')
print(f'Steps Completed: {len(result[\"steps\"])}')
for step in result['steps']:
    print(f'  - {step[\"name\"]}: {step[\"status\"]}')
"
```

## Key Classes and Imports

```python
# Agents
from agents.applicant_agent import ApplicantProfileAgent
from agents.risk_agent import FinancialRiskAnalysisAgent
from agents.decision_agent import LoanDecisionAgent
from agents.orchestrator import LoanApprovalOrchestrator

# MCP Servers
from mcp_servers.applicant_db_server import server as applicant_server
from mcp_servers.risk_rules_db_server import server as risk_server
from mcp_servers.decision_synthesis_server import server as decision_server

# Models
from models.schemas import (
    ApplicantProfile, EmploymentInfo, CreditRecord, LoanDetails,
    LoanApplicationRequest, DecisionClassification
)
```

## Configuration

Environment variables needed (in `.env`):

```bash
LANGSMITH_API_KEY=sk-...                    # Anthropic API key
LANGSMITH_BASE_URL=https://llmgw-wp.tekstac.com
AGENT_TIMEOUT_SECONDS=30                    # Per-agent timeout
WORKFLOW_TIMEOUT_SECONDS=60                 # Total workflow timeout
```

## Expected Performance

- Single agent analysis: 2-3 seconds (includes Claude API call)
- Full workflow (all 3 agents): 5-8 seconds
- Test suite execution: 30-60 seconds

## Output Examples

### Applicant Analysis Output
```python
{
    'validation_status': 'valid',
    'income_stability_score': 78.0,
    'income_stability_level': 'high',
    'employment_risk_score': 15.0,
    'employment_risk_level': 'very_low',
    'credit_summary': {
        'score': 750,
        'score_category': 'Excellent',
        'score_risk_level': 'Very Low',
        ...
    },
    'anomalies': [],
    'reasoning': 'Applicant has excellent credit profile...',
    'profile_completeness': 100.0,
    'critical_issues': [],
    'warnings': [],
    'analyzed_at': '2026-10-29T...'
}
```

### Risk Analysis Output
```python
{
    'risk_score': 22.5,
    'dti_ratio': 24.0,
    'dti_risk_level': 'low',
    'credit_risk': 'low',
    'loan_amount_risk': 'low',
    'anomalies': [],
    'risk_factors': [],
    'positive_factors': [
        'Good debt-to-income ratio',
        'Strong credit profile',
        'Stable employment history',
        'Established credit history',
        'No recent delinquencies'
    ],
    'claude_analysis': 'The applicant demonstrates strong financial stability...',
    'analyzed_at': '2026-10-29T...'
}
```

### Decision Output
```python
{
    'classification': 'approved',
    'classification_value': 'approved',
    'confidence_score': 0.89,
    'reasoning': 'Based on comprehensive analysis, this applicant...',
    'risk_factors': [],
    'positive_factors': [
        'Good debt-to-income ratio',
        'Strong credit profile',
        'Stable employment history'
    ],
    'recommended_interest_rate': 5.5,
    'conditions': [],
    'decided_at': '2026-10-29T...'
}
```

## Debugging

### Enable Debug Logging

```python
import logging
from shared.logger import get_logger

# Get debug logger
logger = get_logger('orchestrator')
logger.setLevel(logging.DEBUG)

# Now orchestrator will log debug information
```

### Check Agent Status

```python
from agents.orchestrator import LoanApprovalOrchestrator

orchestrator = LoanApprovalOrchestrator()
print(f"Applicant Agent: {orchestrator.applicant_agent}")
print(f"Risk Agent: {orchestrator.risk_agent}")
print(f"Decision Agent: {orchestrator.decision_agent}")
```

### Verify Imports Work

```bash
python -c "from agents.decision_agent import LoanDecisionAgent; from agents.orchestrator import LoanApprovalOrchestrator; print('✅ All imports successful')"
```

## Next Steps

After Phase 2 validation:
- Phase 3: API integration with database persistence
- Phase 4: Workflow state persistence and recovery
- Phase 5: Frontend integration with decision display

See `PHASE2_SUMMARY.md` for complete implementation details.
