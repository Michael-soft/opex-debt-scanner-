# 🛡️ OpsEx Debt Scanner

An intelligent operational debt detection system that identifies "silent killer" performance bottlenecks in backend systems using unsupervised machine learning.

## 🎯 Problem Statement

**High latency on 200 OK responses is "Silent Debt"** — it doesn't trigger error alerts, but it silently drains engineering cost and user trust. This tool automatically detects and quantifies the financial impact of performance degradation.

## ✨ Features

### Core Capabilities
- **Unsupervised Anomaly Detection**: Isolation Forest identifies latency anomalies without manual thresholds
- **Financial Impact Quantification**: Calculates wasted engineering hours and direct costs
- **Endpoint-Specific Recommendations**: AI-generated refactoring strategies tailored to each bottleneck
- **Per-Endpoint Analysis**: Breakdown of latency, error rates, and volume by service

### Advanced Analytics
- **Severity Scoring**: 0-100 severity scale for anomalies with distribution visualization
- **ROI Calculations**: Potential savings for each refactoring opportunity
- **Configurable Alerts**: Set thresholds for wasted hours and error rates
- **Real Data Support**: Upload production CSV logs or generate synthetic data

### Data & Insights
- **Baseline Tracking**: Visual reference line for healthy request latency
- **Export Capabilities**: Download anomaly reports as CSV
- **Interactive Dashboards**: Multiple views for trend analysis and drill-down

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/opex-debt-scanner.git
cd opex-debt-scanner

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📊 Usage

### Step 1: Configure Parameters (Sidebar)
- **Data Source**: Choose between synthetic logs or CSV upload
- **Log Volume**: 500-5000 rows (for synthetic data)
- **ML Sensitivity**: 0.01-0.15 contamination (lower = stricter)
- **Engineering Cost**: Set hourly rate (default $60)
- **Alert Thresholds**: Configure notification triggers

### Step 2: Run the Scanner
Click **"Run Scanner"** to:
1. Generate or load system logs
2. Train Isolation Forest anomaly detector
3. Calculate impact metrics
4. Generate refactoring recommendations

### Step 3: Analyze Results
- **KPI Cards**: Overview metrics (total requests, anomalies, wasted hours, financial loss)
- **Latency Scatter Plot**: Visualize performance over time (red = anomalies)
- **Per-Endpoint Analysis**: Bar chart and table showing bottleneck endpoints
- **Executive Agent Report**: AI-generated Kaizen refactoring plans
- **ROI Breakdown**: Potential savings by endpoint
- **Severity Distribution**: Histogram of anomaly impact levels
- **Export Data**: Download findings as CSV

## 🏗️ Architecture

### Four-Layer Design

```
┌─────────────────────────────────────┐
│   UI / Dashboard Layer              │ Streamlit components, charts, metrics
├─────────────────────────────────────┤
│   Executive Agent Layer             │ Refactoring recommendation engine
├─────────────────────────────────────┤
│   Machine Learning Layer            │ Isolation Forest anomaly detection
├─────────────────────────────────────┤
│   Data Engineering Layer            │ Synthetic log generation & transforms
└─────────────────────────────────────┘
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `generate_system_logs()` | Creates synthetic backend logs with debt injection |
| `detect_operational_anomalies()` | Runs Isolation Forest on latency data |
| `run_executive_agent_analysis()` | Pattern matches endpoints to recommendations |
| `calculate_endpoint_metrics()` | Per-endpoint statistical breakdown |
| `calculate_anomaly_severity()` | Scores anomalies on 0-100 scale |
| `calculate_roi_potential()` | Computes savings by fixing each endpoint |

## 📝 Data Format

### Input CSV (for real data)
```csv
Timestamp,Endpoint,Latency_ms,Status
2025-01-12 10:00:00,/api/v1/search/query,150,200
2025-01-12 10:00:01,/api/v1/transactions/process,1800,200
...
```

### Output Data (Downloaded CSV)
```csv
Timestamp,Endpoint,Latency (ms),Wasted (ms),Status
2025-01-12 10:00:01,/api/v1/transactions/process,1800,1650,200
...
```

## 🤖 How It Works

### Anomaly Detection Logic
```python
# 1. Train unsupervised model on latency
model = IsolationForest(contamination=0.05, random_state=42)
df['anomaly'] = model.fit_predict(df[['Latency_ms']])

# 2. Calculate baseline from healthy requests
baseline = normal_requests['Latency_ms'].mean()

# 3. Quantify waste
wasted_ms = (anomaly_latency - baseline) * count
financial_loss = (wasted_ms / 3600000) * hourly_rate
```

### Recommendation Engine
Pattern-matched against endpoint keywords:
- **"search"** → Redis caching + CQRS
- **"report"** → Async job queue + materialized views
- **"transactions"** → Horizontal scaling + circuit breakers
- **Default** → Connection pool analysis + infrastructure review

## 🎯 Real-World Application

### Example Scenario
```
Input: 1000 backend requests (5% artificially slow)
       Detection: 50 anomalies at ~1500ms (vs 150ms baseline)
       Impact: ~8 wasted engineering hours
       Cost: $480 (at $60/hr)
       
Recommendation: 
  → Search endpoints detected
  → Implement Redis caching for `/api/v1/search/query`
  → Potential ROI: $480+ per day in time savings
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: set Streamlit config
export STREAMLIT_LOGGER_LEVEL=warning
export STREAMLIT_CLIENT_SHOWERRORDETAILS=false
```

### Customizing Recommendations
Edit the `run_executive_agent_analysis()` function to add or modify patterns:

```python
elif "custom_endpoint" in worst_endpoint:
    plan = [
        "**Immediate**: Your mitigation strategy",
        "**Root Cause**: Your analysis",
        "**Long Term**: Your solution"
    ]
```

## 📚 Dependencies

- **streamlit** - Web UI framework
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **plotly** - Interactive visualizations
- **scikit-learn** - Isolation Forest ML model

## 📖 Future Enhancements

- [ ] Multi-dimensional anomaly detection (latency + throughput + errors)
- [ ] Integration with real log sources (Datadog, ELK, CloudWatch)
- [ ] Time-series forecasting for trend prediction
- [ ] Automated remediation suggestions using GPT
- [ ] Database storage for historical tracking
- [ ] Team collaboration features
- [ ] PDF report generation
- [ ] Custom alert integrations (Slack, PagerDuty)

## 📄 License

MIT License - See LICENSE file for details

## 🙋 Support

For issues, questions, or feature requests, please open a GitHub issue.

## 👨‍💼 About

Built with the philosophy that **operational debt is often invisible but devastating**. This tool makes it visible and actionable.

---

**Start detecting your silent killers today.** 🛡️
