# Financial Risk Analysis Agent Implementation

## Overview

The Financial Risk Analysis Agent is a sophisticated component of the Intelligent Loan Approval System that performs comprehensive financial risk assessment. It evaluates loan applications based on multiple risk dimensions and synthesizes insights using Claude AI for pattern analysis.

## Architecture

### Core Components

1. **Risk Calculation Engine** - Deterministic calculations for quantitative metrics
2. **Anomaly Detection** - Pattern recognition for unusual applicant profiles
3. **Claude Integration** - AI-powered pattern analysis and risk synthesis
4. **MCP Server** - Tool exposure for inter-agent communication

### Risk Analysis Dimensions

#### 1. Debt-to-Income (DTI) Ratio Analysis
- **Calculation**: (Total Monthly Debt / Monthly Income) × 100
- **Risk Mapping**:
  - DTI < 36%: **Low Risk** (Healthy debt load)
  - DTI 36-43%: **Medium Risk** (Elevated but manageable)
  - DTI > 43%: **High Risk** (Unsustainable debt)

#### 2. Credit Score Risk Mapping
Credit scores are mapped to risk factors with consideration for financial profile:

| Score Range | Risk Level | Risk Factor | Interpretation |
|-------------|-----------|-------------|-----------------|
| 750+ | Low | 0.1 | Excellent credit, minimal risk |
| 700-749 | Low | 0.2 | Good credit, low risk |
| 650-699 | Medium | 0.4 | Fair credit, moderate risk |
| 600-649 | Medium | 0.6 | Poor credit, elevated risk |
| 550-599 | High | 0.8 | Very poor credit, high risk |
| <550 | High | 1.0 | Critical credit issues |

#### 3. Credit Record Details Assessment
Analyzes delinquency patterns, public records, credit history length, and account diversity:
- **Delinquencies** (recent missed payments)
- **Public Records** (bankruptcies, foreclosures, liens)
- **Credit History Length** (minimum 2 years is ideal)
- **Number of Accounts** (diversity indicates credit maturity)

#### 4. Loan Amount Risk Assessment
Evaluates loan amount relative to applicant's financial capacity:

**Loan-to-Income (LTI) Ratios**:
- LTI < 150% (Low risk): Conservative lending
- LTI 150-300% (Medium risk): Moderate exposure
- LTI 300-500% (High risk): Significant exposure
- LTI > 500% (Extreme): Excessive risk

**Loan Term Considerations**:
- Very short terms (< 12 months) with large amounts increase monthly payment risk
- Evaluates payment-to-income ratio for sustainability

#### 5. Anomaly Detection
The agent identifies unusual patterns that may indicate fraud or financial distress:

**Income-Related Anomalies**:
- Significant variance between annual and monthly income (>20%)
- Very recent employment change (<6 months)
- Unemployment or gaps in employment

**Credit-Related Anomalies**:
- Multiple recent delinquencies (> 3 in 24 months)
- Pattern of delinquencies suggesting financial stress
- Unusual debt accumulation

**Loan Request Anomalies**:
- Loan amount excessive relative to income
- Monthly payment unsustainable relative to income
- Unusual loan purpose given profile

### Overall Risk Score Calculation

The agent computes a unified **Risk Score (0-100)** using weighted factors:

**Weights**:
- DTI Analysis: 30%
- Credit Risk: 30%
- Loan Amount Risk: 25%
- Anomalies: 15%

**Risk Categories**:
- 0-40: Low Risk (approval likely)
- 40-70: Medium Risk (requires review)
- 70-100: High Risk (rejection likely or manual review)

## Implementation Details

### File Structure

```
agents/
├── risk_agent.py                    # Main risk analysis agent implementation
mcp_servers/
├── risk_rules_db_server.py         # MCP server for risk assessment tools
tests/
├── test_risk_agent.py              # Unit tests for risk calculations
├── test_risk_integration.py        # Integration tests with different profiles
docs/
├── RISK_AGENT_IMPLEMENTATION.md    # This file
```

### Key Classes

#### FinancialRiskAnalysisAgent

Main agent class providing all risk analysis functionality.

**Initialization**:
```python
from agents.risk_agent import get_risk_agent

agent = get_risk_agent()  # Singleton instance
```

**Key Methods**:

1. **`calculate_dti_ratio(annual_income, monthly_debt_obligations)`**
   - Calculates Debt-to-Income ratio
   - Returns: DTI percentage (0-100)

2. **`assess_dti_risk(dti_ratio)`**
   - Maps DTI ratio to risk level
   - Returns: "low" | "medium" | "high"

3. **`map_credit_score_to_risk(credit_score)`**
   - Maps credit score to risk level and factor
   - Returns: (risk_level, risk_factor)

4. **`assess_credit_risk_details(credit_record)`**
   - Comprehensive credit assessment
   - Returns: dict with risk_level, risk_factors, contribution

5. **`assess_loan_amount_risk(loan_amount, annual_income, current_debt, loan_term_months)`**
   - Evaluates loan amount sustainability
   - Returns: (risk_level, risk_score, risk_factors)

6. **`detect_anomalies(application_data)`**
   - Identifies unusual patterns
   - Returns: List of anomaly descriptions

7. **`analyze_patterns_with_claude(application_data, initial_analysis)`** (async)
   - Uses Claude 3.5 Sonnet for pattern synthesis
   - Returns: dict with Claude's analysis and insights

8. **`calculate_overall_risk_score(...)`**
   - Synthesizes all risk dimensions
   - Returns: Overall risk score (0-100)

9. **`analyze(application)`** (async)
   - Comprehensive risk analysis entry point
   - Returns: Complete risk assessment result

### Risk Analysis Flow

```
Input: LoanApplicationRequest
  │
  ├─→ Extract application data
  │
  ├─→ Calculate DTI ratio
  │   └─→ Determine DTI risk level
  │
  ├─→ Assess credit risk
  │   ├─→ Score-to-risk mapping
  │   └─→ Detailed credit assessment
  │
  ├─→ Assess loan amount risk
  │   ├─→ LTI ratio calculation
  │   ├─→ Total debt evaluation
  │   └─→ Payment sustainability
  │
  ├─→ Detect anomalies
  │   ├─→ Income consistency check
  │   ├─→ Employment stability check
  │   ├─→ Delinquency pattern analysis
  │   └─→ Loan request reasonableness check
  │
  ├─→ Claude Pattern Analysis
  │   ├─→ Send initial analysis to Claude
  │   ├─→ Claude identifies patterns
  │   └─→ Generate synthesis insights
  │
  ├─→ Calculate overall risk score
  │   ├─→ Weight all dimensions
  │   ├─→ Apply multipliers for anomalies
  │   └─→ Normalize to 0-100 scale
  │
  └─→ Output: Complete Risk Assessment
      ├─→ Risk score (0-100)
      ├─→ DTI analysis
      ├─→ Credit assessment
      ├─→ Loan amount evaluation
      ├─→ Anomalies detected
      ├─→ Risk factors
      ├─→ Positive factors
      └─→ Claude's pattern analysis
```

## Usage Examples

### Basic Risk Analysis

```python
import asyncio
from agents.risk_agent import get_risk_agent
from models.schemas import (
    LoanApplicationRequest,
    ApplicantProfile,
    EmploymentInfo,
    CreditRecord,
    LoanDetails,
    EmploymentType,
)

async def analyze_application():
    agent = get_risk_agent()
    
    application = LoanApplicationRequest(
        applicant_profile=ApplicantProfile(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-1234567",
            date_of_birth="1990-01-01",
            ssn="123-45-6789",
            address="123 Main St",
            city="Springfield",
            state="IL",
            zip_code="62701",
        ),
        employment_info=EmploymentInfo(
            employment_type=EmploymentType.FULL_TIME,
            employer_name="Tech Corp",
            job_title="Engineer",
            years_employed=5.0,
            annual_income=85000.0,
            monthly_income=7083.33,
        ),
        credit_record=CreditRecord(
            credit_score=720,
            years_of_credit_history=8.0,
            number_of_accounts=4,
            delinquencies_last_24_months=0,
            public_records=0,
            current_debt=18000.0,
        ),
        loan_details=LoanDetails(
            loan_amount=30000.0,
            loan_purpose="Auto purchase",
            loan_term_months=60,
            interest_rate=5.25,
        ),
    )
    
    result = await agent.analyze(application)
    
    print(f"Risk Score: {result['risk_score']:.1f}")
    print(f"DTI Ratio: {result['dti_ratio']:.2f}%")
    print(f"Risk Level: {result['dti_risk_level']}")
    print(f"Credit Risk: {result['credit_risk']}")
    print(f"Anomalies: {result['anomalies']}")
    print(f"Risk Factors: {result['risk_factors']}")
    print(f"Positive Factors: {result['positive_factors']}")

asyncio.run(analyze_application())
```

### Individual Component Access

```python
from agents.risk_agent import get_risk_agent

agent = get_risk_agent()

# Calculate DTI
dti = agent.calculate_dti_ratio(annual_income=80000, monthly_debt_obligations=2000)
print(f"DTI: {dti:.2f}%")

# Map credit score
risk_level, factor = agent.map_credit_score_to_risk(750)
print(f"Credit Risk: {risk_level}, Factor: {factor}")

# Detect anomalies
app_data = {...}  # application data
anomalies = agent.detect_anomalies(app_data)
print(f"Found {len(anomalies)} anomalies")
```

## Testing

### Running Unit Tests

```bash
cd /home/ubuntu/Desktop/CapStone
pytest tests/test_risk_agent.py -v
```

### Running Integration Tests

```bash
pytest tests/test_risk_integration.py -v
```

### Test Coverage

Run tests with coverage reporting:

```bash
pytest tests/test_risk_agent.py tests/test_risk_integration.py --cov=agents --cov-report=html
```

### Test Scenarios Covered

1. **DTI Calculation**: Various income and debt combinations
2. **Risk Level Mapping**: All risk level transitions
3. **Credit Score Assessment**: Full credit score range
4. **Credit Detail Analysis**: Delinquencies, public records, history length
5. **Loan Amount Risk**: Various LTI ratios and debt levels
6. **Anomaly Detection**: Income mismatches, recent employment, delinquency patterns
7. **Risk Score Calculation**: Component weighting and normalization
8. **Integration Testing**: Complete analysis for different applicant profiles
9. **Performance**: Analysis completion time validation

## MCP Server Integration

### Available Tools

The RiskRulesDB MCP server exposes the following tools:

#### `calculate_dti_ratio`
**Parameters**:
- `annual_income`: float
- `monthly_debt_obligations`: float

**Returns**: DTI ratio and risk level

#### `assess_credit_risk`
**Parameters**:
- `credit_score`: int (300-850)

**Returns**: Credit risk level and risk factor

#### `detect_application_anomalies`
**Parameters**:
- `annual_income`: float
- `monthly_income`: Optional[float]
- `years_employed`: float
- `current_debt`: float
- `delinquencies_24_months`: int
- `loan_amount`: float
- `loan_purpose`: str
- `loan_term_months`: int

**Returns**: List of detected anomalies

#### `assess_loan_amount_risk`
**Parameters**:
- `loan_amount`: float
- `annual_income`: float
- `current_debt`: float
- `loan_term_months`: int

**Returns**: Loan amount risk assessment

#### `calculate_risk_score`
**Parameters**:
- `dti_risk_level`: str
- `credit_risk_level`: str
- `loan_amount_risk_level`: str
- `credit_risk_contribution`: float
- `loan_amount_risk_contribution`: float
- `anomalies_count`: int

**Returns**: Overall risk score (0-100)

#### `get_risk_rules`
**Parameters**: None

**Returns**: Complete risk assessment rules and thresholds

#### `health_check`
**Parameters**: None

**Returns**: Server health status

### Starting the MCP Server

```bash
python -m mcp_servers.risk_rules_db_server
```

## Configuration

Risk assessment is configured via environment variables in `.env`:

```bash
# Agent Configuration
AGENT_TIMEOUT_SECONDS=30
ANTHROPIC_API_KEY=your-api-key

# Model Selection
# Uses Claude 3.5 Sonnet by default for optimal balance
```

## Performance Characteristics

### Benchmarks

- **DTI Calculation**: < 1ms
- **Credit Risk Assessment**: < 5ms
- **Anomaly Detection**: < 10ms
- **Loan Amount Risk**: < 5ms
- **Overall Risk Score**: < 5ms
- **Claude Pattern Analysis**: 1-3 seconds (API call)
- **Complete Analysis**: 2-4 seconds (including Claude)

### Optimization Tips

1. **Cache Claude responses** if applicant profile repeats
2. **Batch anomaly detection** for bulk processing
3. **Pre-calculate thresholds** for rule engine
4. **Use Redis** for risk score caching

## Error Handling

The agent includes comprehensive error handling:

```python
try:
    result = await agent.analyze(application)
except ValueError as e:
    logger.error(f"Invalid application data: {e}")
except asyncio.TimeoutError as e:
    logger.error(f"Claude analysis timeout: {e}")
except Exception as e:
    logger.error(f"Unexpected error in risk analysis: {e}")
    # Return partial results with available data
```

## Compliance Considerations

The agent is designed with compliance in mind:

1. **Audit Trail**: All risk assessments logged with timestamps
2. **Deterministic Calculations**: Debt, income, and credit calculations are reproducible
3. **Explainability**: All risk factors clearly documented
4. **Regulatory Thresholds**: DTI, credit score mappings based on industry standards
5. **Fair Lending**: Equal treatment regardless of protected class

## Future Enhancements

### Phase 3+

1. **Historical Pattern Learning**: Analyze historical approval/rejection rates
2. **Market-Based Adjustments**: Incorporate regional economic indicators
3. **Alternative Credit Models**: Support for non-traditional credit data
4. **Real-Time Market Data**: Interest rate adjustment recommendations
5. **Predictive Modeling**: ML-based risk prediction (vs. rule-based)
6. **Federated Learning**: Privacy-preserving pattern sharing across institutions

### Integration Points

- **Orchestrator**: Receives analysis results for decision synthesis
- **Decision Agent**: Uses risk scores for classification
- **Compliance Agent**: Provides audit trail details
- **API Layer**: Exposes risk assessment endpoint

## Troubleshooting

### Common Issues

**Issue**: High API costs for Claude integration
**Solution**: 
- Implement response caching
- Use cheaper model for non-critical analyses
- Batch process similar applications

**Issue**: Timeouts during Claude analysis
**Solution**:
- Increase `AGENT_TIMEOUT_SECONDS`
- Optimize prompt length
- Implement fallback to rule-based analysis

**Issue**: DTI calculations seem incorrect
**Solution**:
- Verify income and debt values include all sources
- Check monthly debt includes new loan payment
- Validate credit record current_debt value

## References

- [Debt-to-Income Standards](https://www.investopedia.com/terms/d/dti.asp)
- [Credit Score Ranges](https://www.investopedia.com/terms/c/credit_score.asp)
- [Fair Lending Practices](https://www.fdic.gov/resources/consumers/consumer-topics/fair-lending-practices/)
- [Risk Assessment Frameworks](https://www.bis.org/bcbs/index.htm)
