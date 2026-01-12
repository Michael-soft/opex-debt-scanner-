
from __future__ import annotations

import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from sklearn.ensemble import IsolationForest # type: ignore
from datetime import datetime, timedelta
import io

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OpsEx Debt Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Fintech" professional look
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-ok { color: #09ab3b; font-weight: bold; }
    .status-debt { color: #ff4b4b; font-weight: bold; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA ENGINEERING LAYER (Synthetic Log Generation)
# -----------------------------------------------------------------------------
@st.cache_data
def generate_system_logs(n_rows: int = 1000, debt_ratio: float = 0.05) -> pd.DataFrame:
    """
    Generates synthetic backend logs.
    Injects 'Operational Debt' by making a % of requests significantly slower
    but still returning status 200 (The 'Silent Killer').
    """
    
    endpoints = [
        '/api/v1/auth/login', 
        '/api/v1/transactions/process', 
        '/api/v1/reports/generate', 
        '/api/v1/user/profile', 
        '/api/v1/search/query'
    ]
    
    # Base timestamps
    base_time = datetime.now()
    timestamps = [base_time - timedelta(seconds=i*2) for i in range(n_rows)]
    
    data: list[dict[str, any]] = []
    
    for ts in timestamps:
        endpoint = np.random.choice(endpoints, p=[0.3, 0.2, 0.1, 0.2, 0.2])
        is_debt = np.random.random() < debt_ratio
        
        # Logic: Normal requests are fast (50-300ms). Debt requests are slow (1000-2500ms)
        if is_debt:
            # Operational Debt: Slow but successful
            latency = int(np.random.normal(1500, 300))
            status = 200 
            log_type = "Hidden Debt"
        else:
            # Standard Traffic
            latency = int(np.random.normal(150, 50))
            # Occasional actual errors
            if np.random.random() < 0.01:
                status = 500
                log_type = "Hard Error"
            else:
                status = 200
                log_type = "Healthy"
        
        # Ensure non-negative latency
        latency = max(10, latency)
        
        data.append({
            'Timestamp': ts,
            'Endpoint': endpoint,
            'Latency_ms': latency,
            'Status': status,
            'True_Label': log_type # Hidden from ML model, used for validation visualization if needed
        })
        
    df = pd.DataFrame(data)
    df = df.sort_values('Timestamp')
    return df

# -----------------------------------------------------------------------------
# 3. MACHINE LEARNING LAYER (Anomaly Detection)
# -----------------------------------------------------------------------------
def detect_operational_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """
    Uses Isolation Forest to detect latency anomalies without manual rules.
    """
    model = IsolationForest(contamination=contamination, random_state=42)
    
    # We only care about Latency for this specific debt scan
    # In a real app, we might encode Endpoint as a feature too
    X = df[['Latency_ms']]
    
    df['anomaly_score'] = model.fit_predict(X)
    
    # IsolationForest: -1 is anomaly, 1 is normal. Map to boolean/string for UI.
    df['is_anomaly'] = df['anomaly_score'].map({1: False, -1: True})
    
    return df

# -----------------------------------------------------------------------------
# 4. OPEX STRATEGY AGENT (Simulated Executive Logic)
# -----------------------------------------------------------------------------
def run_executive_agent_analysis(df_anomalies: pd.DataFrame) -> tuple[str, list[str]]:
    """
    Analyzes the specific nature of the anomalies to recommend a 
    Kaizen Refactoring Plan.
    """
    if df_anomalies.empty:
        return "No significant debt detected. Systems operational.", []

    # Identify the endpoint causing the most wasted time
    worst_endpoint = df_anomalies.groupby('Endpoint')['Latency_ms'].sum().idxmax()
    avg_latency = df_anomalies[df_anomalies['Endpoint'] == worst_endpoint]['Latency_ms'].mean()
    
    plan = []
    
    # Logic-based recommendations
    if "search" in worst_endpoint:
        plan = [
            f"**Immediate Mitigation:** Implement **Redis Caching** layer for `{worst_endpoint}` to serve frequent queries from memory.",
            "**Root Cause Analysis:** ElasticSearch indices likely unoptimized or mapping explosion occurring.",
            "**Long Term:** Shift to an event-driven projection pattern (CQRS) for read-heavy search loads."
        ]
    elif "report" in worst_endpoint:
        plan = [
            f"**Immediate Mitigation:** Move `{worst_endpoint}` to an **Async Job Queue** (Celery/BullMQ). Do not block HTTP threads.",
            "**Database Optimization:** Analyze `EXPLAIN ANALYZE` for missing composite indexes on report filters.",
            "**Long Term:** Implement Materialized Views (BigQuery/Postgres) refreshed hourly."
        ]
    elif "transactions" in worst_endpoint:
        plan = [
            f"**Immediate Mitigation:** Scale horizontal pods for `{worst_endpoint}` and audit external API dependency timeouts.",
            "**Code Review:** Check for N+1 query problems in the transaction ORM layer.",
            "**Architecture:** Isolate transaction processing into a dedicated microservice with circuit breakers."
        ]
    else:
        plan = [
            f"**Immediate Mitigation:** Review application logs for `{worst_endpoint}` during high-latency windows.",
            "**Infrastructure:** Check CPU steal/Memory saturation on host nodes.",
            "**Pattern:** Likely connection pool exhaustion. Increase max_pool_size or implement connection multiplexing (PgBouncer)."
        ]
        
    return worst_endpoint, plan

# -----------------------------------------------------------------------------
# 5. ADVANCED ANALYTICS LAYER
# -----------------------------------------------------------------------------
def calculate_endpoint_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates per-endpoint metrics for detailed analysis.
    """
    metrics = df.groupby('Endpoint').agg({
        'Latency_ms': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'Status': lambda x: (x == 500).sum()
    }).round(2)
    
    metrics.columns = ['Mean_Latency', 'Median_Latency', 'Std_Dev', 
                       'Min_Latency', 'Max_Latency', 'Total_Requests', 'Error_Count']
    metrics['Error_Rate'] = (metrics['Error_Count'] / metrics['Total_Requests'] * 100).round(2)
    
    return metrics.reset_index()

def calculate_anomaly_severity(anomalies: pd.DataFrame, baseline: float) -> pd.DataFrame:
    """
    Calculates severity score for each anomaly (0-100).
    """
    anomalies_copy = anomalies.copy()
    anomalies_copy['Severity_Score'] = (
        ((anomalies_copy['Latency_ms'] - baseline) / baseline * 100)
        .clip(0, 100)
        .round(1)
    )
    return anomalies_copy

def calculate_roi_potential(anomalies: pd.DataFrame, baseline: float, hourly_rate: float) -> dict[str, float]:
    """
    Calculates potential ROI of fixing each type of bottleneck.
    """
    roi_data = {}
    
    for endpoint in anomalies['Endpoint'].unique():
        endpoint_anomalies = anomalies[anomalies['Endpoint'] == endpoint]
        wasted_ms = (endpoint_anomalies['Latency_ms'] - baseline).sum()
        wasted_hours = wasted_ms / (1000 * 60 * 60)
        potential_savings = wasted_hours * hourly_rate
        
        roi_data[endpoint] = {
            'wasted_hours': round(wasted_hours, 2),
            'potential_savings': round(potential_savings, 2)
        }
    
    return roi_data

# -----------------------------------------------------------------------------
# MAIN APP EXECUTION
# -----------------------------------------------------------------------------

def main() -> None:
    # --- Sidebar ---
    st.sidebar.title("⚙️ OpsEx Control Plane")
    st.sidebar.markdown("Define simulation parameters.")
    
    # Data source selection
    data_source = st.sidebar.radio("📊 Data Source", ["Generate Synthetic", "Upload CSV"])
    
    if data_source == "Generate Synthetic":
        n_logs = st.sidebar.slider("Log Volume (Rows)", 500, 5000, 1000)
        debt_ratio = st.sidebar.slider("Debt Injection Rate (%)", 1, 20, 5) / 100
    else:
        uploaded_file = st.sidebar.file_uploader("Upload CSV with columns: Timestamp, Endpoint, Latency_ms, Status")
        debt_ratio = 0
    
    contamination = st.sidebar.slider("ML Sensitivity (Contamination)", 0.01, 0.15, 0.05)
    hourly_rate = st.sidebar.number_input("Eng. Cost per Hour ($)", value=60, min_value=10)
    
    # Alert thresholds
    with st.sidebar.expander("⚠️ Alert Thresholds"):
        wasted_hours_threshold = st.number_input("Alert if wasted hours > ", value=5.0)
        error_rate_threshold = st.number_input("Alert if error rate > (%)", value=1.0)
    
    if st.sidebar.button("Run Scanner", type="primary"):
        st.session_state['run_analysis'] = True
    
    st.sidebar.markdown("---")
    st.sidebar.info("**Philosophy:** High latency on 200 OK responses is 'Silent Debt'. It doesn't trigger error alerts, but it burns money and trust.")

    # --- Header ---
    st.title("🛡️ Automated Operational Debt Scanner")
    st.markdown("### Detect. Quantify. Refactor.")
    st.markdown("This tool ingests system logs, uses Unsupervised Learning to identify silent performance degradation, and generates a refactoring roadmap.")

    if st.session_state.get('run_analysis'):
        with st.spinner("Ingesting logs & training Isolation Forest..."):
            
            # 1. Generate or Load Data
            if data_source == "Generate Synthetic":
                raw_df = generate_system_logs(n_rows=n_logs, debt_ratio=debt_ratio)
            else:
                if uploaded_file:
                    raw_df = pd.read_csv(uploaded_file)
                    raw_df['Timestamp'] = pd.to_datetime(raw_df['Timestamp'])
                else:
                    st.error("Please upload a CSV file")
                    return
            
            # 2. Run ML
            processed_df = detect_operational_anomalies(raw_df.copy(), contamination)
            
            # 3. Calculate Impact
            anomalies = processed_df[processed_df['is_anomaly'] == True]
            normal = processed_df[processed_df['is_anomaly'] == False]
            
            if normal.empty:
                baseline_latency = processed_df['Latency_ms'].quantile(0.25)
            else:
                baseline_latency = normal['Latency_ms'].mean()
            
            # Wasted time = (Anomaly Latency - Baseline Latency)
            anomalies_calc = anomalies.copy()
            anomalies_calc['Wasted_ms'] = (anomalies_calc['Latency_ms'] - baseline_latency).clip(lower=0)
            total_wasted_ms = anomalies_calc['Wasted_ms'].sum()
            total_wasted_hours = total_wasted_ms / (1000 * 60 * 60)
            financial_loss = total_wasted_hours * hourly_rate

        # --- Dashboard UI ---
        
        # Row 1: KPI Cards with Alerts
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Requests Scan", f"{len(processed_df):,}")
        c2.metric("Silent Anomalies", f"{len(anomalies)}", delta=f"-{len(anomalies)/len(processed_df):.1%}", delta_color="inverse")
        c3.metric("Wasted Eng. Time", f"{total_wasted_hours:.2f} hrs")
        c4.metric("Est. Financial Loss", f"${financial_loss:,.2f}", delta_color="inverse")
        
        # Alert boxes
        alert_cols = st.columns(2)
        with alert_cols[0]:
            if total_wasted_hours > wasted_hours_threshold:
                st.warning(f"⚠️ **High Debt Alert**: {total_wasted_hours:.2f} hrs > {wasted_hours_threshold:.1f} hrs threshold")
        
        with alert_cols[1]:
            error_rate = (processed_df['Status'] == 500).sum() / len(processed_df) * 100
            if error_rate > error_rate_threshold:
                st.error(f"🔴 **High Error Rate**: {error_rate:.2f}% > {error_rate_threshold:.1f}% threshold")

        # Row 2: Latency Visualization
        st.subheader("🔍 Latency Scatter Plot (Anomaly Detection)")
        
        fig = px.scatter(
            processed_df, 
            x="Timestamp", 
            y="Latency_ms", 
            color="is_anomaly",
            color_discrete_map={False: "#09ab3b", True: "#ff4b4b"},
            hover_data=['Endpoint', 'Status'],
            title="System Latency over Time (Red = Detected Debt)"
        )
        fig.add_hline(y=baseline_latency, line_dash="dash", line_color="blue", 
                      annotation_text=f"Baseline: {baseline_latency:.0f}ms")
        fig.update_layout(xaxis_title="Time", yaxis_title="Latency (ms)", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Row 3: Endpoint Breakdown
        st.subheader("📊 Per-Endpoint Analysis")
        endpoint_metrics = calculate_endpoint_metrics(processed_df)
        endpoint_metrics_sorted = endpoint_metrics.sort_values('Mean_Latency', ascending=False)
        
        col_chart, col_table = st.columns([1.2, 1])
        
        with col_chart:
            fig_endpoints = px.bar(
                endpoint_metrics_sorted,
                x='Endpoint',
                y='Mean_Latency',
                color='Error_Rate',
                color_continuous_scale='RdYlGn_r',
                title='Mean Latency by Endpoint',
                hover_data=['Total_Requests', 'Error_Rate']
            )
            st.plotly_chart(fig_endpoints, use_container_width=True)
        
        with col_table:
            st.dataframe(endpoint_metrics_sorted[['Endpoint', 'Mean_Latency', 'Error_Rate', 'Total_Requests']], 
                        use_container_width=True, hide_index=True)

        # Row 4: Strategy & Details
        col_strategy, col_data = st.columns([1, 1])

        with col_strategy:
            st.subheader("🤖 Executive Agent Report")
            worst_ep, steps = run_executive_agent_analysis(anomalies_calc)
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🛑 Primary Offender: <code>{worst_ep}</code></h4>
                <p>The AI has detected that this endpoint contributes most significantly to operational drag.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 📋 Kaizen Refactoring Plan")
            for i, step in enumerate(steps, 1):
                st.markdown(f"**{i}.** {step}")
            
            # ROI Calculation
            roi_data = calculate_roi_potential(anomalies_calc, baseline_latency, hourly_rate)
            if roi_data:
                st.markdown("#### 💰 Potential Savings by Endpoint")
                for endpoint, metrics in sorted(roi_data.items(), key=lambda x: x[1]['potential_savings'], reverse=True):
                    st.metric(endpoint, f"${metrics['potential_savings']:,.2f}", 
                             f"{metrics['wasted_hours']:.1f} wasted hrs")

        with col_data:
            st.subheader("📝 Raw Anomaly Data")
            anomalies_display = anomalies_calc[['Timestamp', 'Endpoint', 'Latency_ms', 'Wasted_ms', 'Status']].copy()
            anomalies_display.columns = ['Timestamp', 'Endpoint', 'Latency (ms)', 'Wasted (ms)', 'Status']
            st.dataframe(
                anomalies_display.sort_values('Latency (ms)', ascending=False),
                height=300,
                use_container_width=True,
                hide_index=True
            )
        
        # Row 5: Export & Severity Distribution
        st.divider()
        
        exp_col1, exp_col2 = st.columns(2)
        
        with exp_col1:
            st.subheader("📥 Export Report")
            # CSV export
            csv_buffer = io.StringIO()
            anomalies_display.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📊 Download Anomalies (CSV)",
                data=csv_data,
                file_name=f"debt_scanner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with exp_col2:
            st.subheader("📈 Severity Distribution")
            anomalies_severity = calculate_anomaly_severity(anomalies_calc, baseline_latency)
            
            fig_severity = go.Figure(data=[
                go.Histogram(x=anomalies_severity['Severity_Score'], nbinsx=20, 
                            marker_color='#ff4b4b', name='Severity')
            ])
            fig_severity.update_layout(
                title='Anomaly Severity Score Distribution',
                xaxis_title='Severity Score (0-100)',
                yaxis_title='Count',
                height=300
            )
            st.plotly_chart(fig_severity, use_container_width=True)

    else:
        st.info("👈 Use the sidebar to configure parameters and run the Operational Debt Scanner.")
        
        # Placeholder view
        st.markdown("---")
        st.markdown("#### ✨ New Features")
        st.markdown("""
        - 📤 **Upload CSV**: Analyze real backend logs
        - 📊 **Per-Endpoint Analysis**: Identify worst performers
        - 💰 **ROI Calculations**: See savings potential
        - ⚠️ **Alert Thresholds**: Get notified of critical issues
        - 📥 **Export Reports**: Download findings as CSV
        - 📈 **Severity Scoring**: Understand anomaly impact
        """)
        
        st.markdown("#### 🔍 How It Works")
        st.code("""
# The Core Logic:
model = IsolationForest(contamination=0.05)
df['anomaly'] = model.fit_predict(df[['latency']])
financial_loss = calculate_waste(df[df['anomaly']==-1])
roi = calculate_potential_savings_per_endpoint()
        """, language="python")

if __name__ == "__main__":
    main()