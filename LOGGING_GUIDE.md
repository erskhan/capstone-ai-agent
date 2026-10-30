# 📋 Logging Guide - Loan Approval System

## Overview

The application now includes comprehensive logging to monitor background processing of loan applications. All logs are displayed in the terminal with color-coded levels and correlation IDs for request tracking.

## Running the Backend with Visible Logs

### Option 1: Using the Provided Script (Recommended)

```bash
cd /home/ubuntu/Desktop/CapStone
./run_backend_with_logs.sh
```

### Option 2: Direct Command

```bash
LOG_LEVEL=INFO /home/ubuntu/anthropic-env/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Save Logs to File and Terminal

```bash
LOG_LEVEL=INFO /home/ubuntu/anthropic-env/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee backend.log
```

## Log Format

All logs follow this format:

```
[TIMESTAMP] [LEVEL    ] module_name: message | correlation_id=xxxxx
```

**Example:**
```
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Received loan application | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
```

## Log Levels

- 🔵 **INFO** (Green) - Normal operation events
- 🟡 **WARNING** (Yellow) - Non-critical issues
- 🔴 **ERROR** (Red) - Critical errors that need attention
- 🟣 **CRITICAL** (Magenta) - System-level failures
- 🔷 **DEBUG** (Cyan) - Detailed diagnostic information

## What to Look For

### Application Submission

When a user submits an application from the Streamlit frontend:

```
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Received loan application | correlation_id=679e4470-...
[2026-10-30 20:21:59] [INFO    ] loan_approval.db_service: Created workflow execution for application ce11d4cf...
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Queued orchestration for ce11d4cf... | correlation_id=679e4470-...
```

### Background Processing Starts

```
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Background: Starting orchestration for ce11d4cf... | correlation_id=679e4470-...
[2026-10-30 20:21:59] [INFO    ] loan_approval.orchestrator: Starting async application processing: ce11d4cf... | correlation_id=679e4470-...
```

### Parallel Agent Execution

Applicant and Risk agents run in parallel:

```
[2026-10-30 20:21:59] [INFO    ] loan_approval.applicant_agent: Starting applicant profile analysis for test@example.com
[2026-10-30 20:21:59] [INFO    ] loan_approval.risk_agent: Starting financial risk analysis
[2026-10-30 20:22:05] [INFO    ] loan_approval.applicant_agent: Applicant profile analysis completed for test@example.com
[2026-10-30 20:22:10] [INFO    ] loan_approval.risk_agent: Financial risk analysis completed
```

### Decision Making

```
[2026-10-30 20:22:10] [INFO    ] loan_approval.orchestrator: Starting decision synthesis | correlation_id=679e4470-...
[2026-10-30 20:22:10] [INFO    ] loan_approval.decision_agent: Starting loan decision synthesis for test@example.com
[2026-10-30 20:22:14] [INFO    ] loan_approval.decision_agent: Loan decision completed for test@example.com
[2026-10-30 20:22:14] [INFO    ] loan_approval.orchestrator: Decision synthesis completed: approved | correlation_id=679e4470-...
```

### Compliance & Notifications

```
[2026-10-30 20:22:14] [INFO    ] loan_approval.orchestrator: Starting compliance validation | correlation_id=679e4470-...
[2026-10-30 20:22:16] [INFO    ] loan_approval.compliance_agent: Compliance validation completed for ce11d4cf...
[2026-10-30 20:22:16] [INFO    ] loan_approval.notification_agent: Queued 2 notifications for ce11d4cf...
```

### Completion

```
[2026-10-30 20:22:16] [INFO    ] loan_approval.orchestrator: Async application processing completed successfully: ce11d4cf... | correlation_id=679e4470-...
[2026-10-30 20:22:16] [INFO    ] loan_approval.main: Background: Orchestration completed for ce11d4cf... | correlation_id=679e4470-...
```

## Workflow Processing Timeline

Here's the typical sequence when an application is submitted:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Application Submitted via Streamlit                      │
│    └─ API creates application record & queues background    │
│       task                                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Background Orchestration Starts                          │
│    (can take 10-30 seconds)                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Parallel Analysis (runs simultaneously)                  │
│    ├─ Applicant Agent (profile validation)   ~3-5 seconds   │
│    └─ Risk Agent (financial analysis)        ~3-5 seconds   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Decision Synthesis                                       │
│    └─ Decision Agent (approve/reject)        ~4 seconds     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Compliance Validation                                    │
│    └─ Compliance Agent (regulatory checks)   ~2 seconds     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Notifications Queued                                     │
│    └─ Notification Agent (email/SMS)         ~1 second      │
└─────────────────────────────────────────────────────────────┘
                            ↓
              ✅ Processing Complete
            (Total time: ~15-20 seconds)
```

## Troubleshooting

### Logs Not Appearing

**Issue:** You submit an application but don't see logs in the terminal.

**Solution:**
1. Check that the backend is running: `ps aux | grep uvicorn`
2. Ensure LOG_LEVEL is set to INFO: `echo $LOG_LEVEL`
3. Make sure port 8000 is accessible: `curl http://localhost:8000/health`

### Logs Showing Only API Messages

**Issue:** You see HTTP logs but not application processing logs.

**Solution:**
1. The logs are there but you need to scroll up to see them
2. Use `tail -f backend.log` if running with file output
3. Check correlation_id matches between API and orchestrator logs

### Errors in Background Processing

**Issue:** Application submitted successfully but logs show errors in orchestration.

**Solution:**
1. Check the error message - it will indicate which agent failed
2. Look for exception details in red logs (ERROR level)
3. Check the correlation_id to track the specific application
4. The application status is still saved to database even if processing fails

## Configuration

### Change Log Level

Edit environment variable before starting:

```bash
LOG_LEVEL=DEBUG /home/ubuntu/anthropic-env/bin/uvicorn backend.main:app --reload
```

Available levels:
- `DEBUG` - Most verbose, includes detailed agent operations
- `INFO` - Normal level, shows main events
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

### Enable File Logging

To also save logs to a file:

```bash
LOG_LEVEL=INFO /home/ubuntu/anthropic-env/bin/uvicorn backend.main:app --reload 2>&1 | tee backend.log
```

Then view in another terminal:

```bash
tail -f backend.log
```

## Viewing Logs in Real-Time

### Terminal 1: Start Backend

```bash
cd /home/ubuntu/Desktop/CapStone
./run_backend_with_logs.sh
```

### Terminal 2: Submit Application & Watch Logs

```bash
# In another terminal, submit an application via curl or Streamlit UI
# Watch Terminal 1 for real-time logs as the application processes
```

## Correlation ID Tracking

Each application request gets a unique `correlation_id` that appears in all related logs. This helps you trace an entire application through all processing steps.

**Example workflow with correlation_id:**

```
679e4470-8d3a-449b-ba56-6c19932bd051  ← Application ID
│
├─ Main API receives: [INFO] Received loan application | correlation_id=679e4470-...
├─ Orchestrator starts: [INFO] Starting async application processing: ... | correlation_id=679e4470-...
├─ Applicant Agent: [INFO] Starting applicant profile analysis ... (no correlation_id in agent logs)
├─ Risk Agent: [INFO] Starting financial risk analysis (no correlation_id in agent logs)
├─ Decision Agent: [INFO] Loan decision completed for ... (no correlation_id in agent logs)
├─ Compliance Agent: [INFO] Compliance validation completed ... (no correlation_id in agent logs)
├─ Notification Agent: [INFO] Queued 2 notifications ... (no correlation_id in agent logs)
└─ Main completes: [INFO] Background: Orchestration completed | correlation_id=679e4470-...
```

You can grep for the correlation_id to see all logs related to that application:

```bash
grep "679e4470-8d3a-449b-ba56-6c19932bd051" backend.log
```

## Live Example

When you submit an application, you'll see something like this in your terminal:

```
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Received loan application | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:21:59] [INFO    ] loan_approval.db_service: Created workflow execution for application ce11d4cf-55a3-4f18-9166-3f6898b8c50f | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Queued orchestration for ce11d4cf-55a3-4f18-9166-3f6898b8c50f | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Background: Starting orchestration for ce11d4cf-55a3-4f18-9166-3f6898b8c50f | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:21:59] [INFO    ] loan_approval.orchestrator: Starting async application processing: ce11d4cf-55a3-4f18-9166-3f6898b8c50f | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:21:59] [INFO    ] loan_approval.orchestrator: Starting parallel applicant and risk analysis | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:21:59] [INFO    ] loan_approval.applicant_agent: Starting applicant profile analysis for test@example.com
[2026-10-30 20:21:59] [INFO    ] loan_approval.risk_agent: Starting financial risk analysis
... (waiting ~5 seconds for analysis to complete)
[2026-10-30 20:22:05] [INFO    ] loan_approval.applicant_agent: Applicant profile analysis completed for test@example.com
[2026-10-30 20:22:10] [INFO    ] loan_approval.risk_agent: Financial risk analysis completed
[2026-10-30 20:22:10] [INFO    ] loan_approval.orchestrator: Parallel analysis completed in 10.47s | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:22:10] [INFO    ] loan_approval.decision_agent: Starting loan decision synthesis for test@example.com
... (waiting ~4 seconds for decision)
[2026-10-30 20:22:14] [INFO    ] loan_approval.decision_agent: Loan decision completed for test@example.com
[2026-10-30 20:22:14] [INFO    ] loan_approval.compliance_agent: Starting compliance validation for ce11d4cf-55a3-4f18-9166-3f6898b8c50f
... (waiting ~2 seconds for compliance)
[2026-10-30 20:22:16] [INFO    ] loan_approval.compliance_agent: Compliance validation completed for ce11d4cf-55a3-4f18-9166-3f6898b8c50f
[2026-10-30 20:22:16] [INFO    ] loan_approval.notification_agent: Queued 2 notifications for ce11d4cf-55a3-4f18-9166-3f6898b8c50f
[2026-10-30 20:22:16] [INFO    ] loan_approval.orchestrator: Async application processing completed successfully: ce11d4cf-55a3-4f18-9166-3f6898b8c50f | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051
[2026-10-30 20:22:16] [INFO    ] loan_approval.main: Background: Orchestration completed for ce11d4cf-55a3-4f18-9166-3f6898b8c50f | correlation_id=679e4470-8d3a-449b-ba56-6c19932bd051

✅ Application processing complete!
```

## Summary

✅ **What's Changed:**
- Improved console logging with color-coded output
- Better readability with timestamps and module names
- Correlation IDs for tracking applications through the system
- Easy-to-use script for running the backend with visible logs

✅ **When to Use:**
- During development to monitor agent processing
- For debugging application rejections
- To understand workflow timing
- To verify all agents are running correctly

Enjoy watching your AI agents process loan applications in real-time! 🚀
