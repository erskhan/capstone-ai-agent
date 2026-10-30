# 🚀 Quick Start - Terminal Logs

## See Logs in Real-Time

### 1. Start Backend with Visible Logs
```bash
cd /home/ubuntu/Desktop/CapStone
./run_backend_with_logs.sh
```

### 2. In Another Terminal - Start Streamlit App
```bash
cd /home/ubuntu/Desktop/CapStone/frontend
streamlit run app.py
```

### 3. Submit Application via Streamlit UI
- Login with your email
- Click "📝 Submit Application"
- Fill out the form and submit
- Watch the **first terminal** for real-time logs!

---

## What You'll See in Terminal

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND TERMINAL                         │
│  (Watch this while application processes)                   │
└─────────────────────────────────────────────────────────────┘

[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Received loan application
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Queued orchestration for ce11d4cf...
[2026-10-30 20:21:59] [INFO    ] loan_approval.main: Background: Starting orchestration
[2026-10-30 20:21:59] [INFO    ] loan_approval.orchestrator: Starting async application processing
[2026-10-30 20:21:59] [INFO    ] loan_approval.orchestrator: Starting parallel applicant and risk analysis
┌─ [2026-10-30 20:21:59] [INFO    ] loan_approval.applicant_agent: Starting applicant profile analysis
├─ [2026-10-30 20:21:59] [INFO    ] loan_approval.risk_agent: Starting financial risk analysis
│
├─ ... (processing for ~5 seconds) ...
│
├─ [2026-10-30 20:22:05] [INFO    ] loan_approval.applicant_agent: Applicant profile analysis completed
└─ [2026-10-30 20:22:10] [INFO    ] loan_approval.risk_agent: Financial risk analysis completed

[2026-10-30 20:22:10] [INFO    ] loan_approval.orchestrator: Parallel analysis completed in 10.47s
[2026-10-30 20:22:10] [INFO    ] loan_approval.orchestrator: Starting decision synthesis
[2026-10-30 20:22:10] [INFO    ] loan_approval.decision_agent: Starting loan decision synthesis
┌─ ... (processing for ~4 seconds) ...
└─ [2026-10-30 20:22:14] [INFO    ] loan_approval.decision_agent: Loan decision completed

[2026-10-30 20:22:14] [INFO    ] loan_approval.orchestrator: Decision synthesis completed: approved
[2026-10-30 20:22:14] [INFO    ] loan_approval.orchestrator: Starting compliance validation
┌─ ... (processing for ~2 seconds) ...
└─ [2026-10-30 20:22:16] [INFO    ] loan_approval.compliance_agent: Compliance validation completed

[2026-10-30 20:22:16] [INFO    ] loan_approval.orchestrator: Starting notification queuing
[2026-10-30 20:22:16] [INFO    ] loan_approval.notification_agent: Queued 2 notifications
[2026-10-30 20:22:16] [INFO    ] loan_approval.orchestrator: Async application processing completed successfully
[2026-10-30 20:22:16] [INFO    ] loan_approval.main: Background: Orchestration completed

✅ Application processing complete! (Total time: ~17 seconds)
```

---

## Color Meanings

```
🟢 GREEN [INFO]      = Normal processing step
🟡 YELLOW [WARNING]  = Something unusual but OK
🔴 RED [ERROR]       = Problem occurred
🟪 MAGENTA [CRITICAL]= System critical failure
🔷 CYAN [DEBUG]      = Detailed diagnostic info
```

---

## Timeline

```
T+0s    Application submitted from Streamlit
        ↓
T+0s    Backend receives & queues background task
        ↓
T+1s    Background processing starts
        ├─ Applicant Agent begins
        └─ Risk Agent begins (parallel)
        ↓
T+5s    Both agents complete
        ↓
T+5s    Decision Agent begins
        ↓
T+9s    Decision Agent completes
        ↓
T+9s    Compliance Agent begins
        ↓
T+11s   Compliance Agent completes
        ↓
T+11s   Notification Agent begins
        ↓
T+12s   All notifications queued
        ↓
T+12s   ✅ PROCESSING COMPLETE (18 seconds total)
```

---

## Commands Quick Reference

| Task | Command |
|------|---------|
| Start backend with logs | `./run_backend_with_logs.sh` |
| Start Streamlit app | `cd frontend && streamlit run app.py` |
| View logs in new terminal | `tail -f backend.log` |
| Filter logs by app ID | `grep "ce11d4cf" backend.log` |
| Stop backend | `Ctrl+C` in backend terminal |
| Stop Streamlit | `Ctrl+C` in Streamlit terminal |

---

## Verify Everything Works

### Test 1: Backend Running
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"0.1.0"}
```

### Test 2: API Responding
```bash
curl http://localhost:8000/api/applications?limit=5
# Should return: {"total":...,"applications":[...]}
```

### Test 3: Logs Working
- Submit an application via Streamlit
- Watch backend terminal for logs appearing in real-time
- Should see at least 10+ log lines over ~15-20 seconds

---

## For More Details

📖 Full logging guide: `LOGGING_GUIDE.md`
📖 Implementation summary: `IMPLEMENTATION_SUMMARY.md`

---

## Need Help?

1. **Logs not showing?**
   - Check backend is running: `ps aux | grep uvicorn`
   - Check port 8000: `lsof -i :8000`
   - Check LOG_LEVEL: `echo $LOG_LEVEL` (should be INFO)

2. **Application not processing?**
   - Check Streamlit is connected to backend
   - Check Streamlit secrets file exists: `frontend/.streamlit/secrets.toml`
   - Check API_URL is correct: should be `http://localhost:8000`

3. **Logs mixed up?**
   - Scroll up in terminal to see complete flow
   - Use `grep` to filter by correlation_id
   - Each application gets unique ID for tracking

---

**Ready? Run `./run_backend_with_logs.sh` and watch the magic! 🎉**
