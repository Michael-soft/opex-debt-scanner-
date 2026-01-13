"""
OpsEx Debt Scanner - Automated Operational Debt Detection
Author: Michael Software
Version: 2.0

This is the refactored, modular version with enhanced analytics.
See config.py, validators.py, metrics.py, strategies.py for modules.
"""

from __future__ import annotations

import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from sklearn.ensemble import IsolationForest # type: ignore
from datetime import datetime, timedelta
import io
import logging

# Import modular components
import config
from validators import validate_csv, clean_data
from metrics import (
    calculate_endpoint_metrics,
    calculate_percentiles,
    calculate_anomaly_severity,
    calculate_roi_potential,
    calculate_latency_trends,
    find_peak_hours,
    calculate_sla_compliance,
    generate_health_score
)
from strategies import get_strategy_for_endpoint, get_quick_wins, evaluate_against_sla

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------
# 1. CONFIGURATION & STYLING
# -----------------------------------------------
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state=config.SIDEBAR_STATE
)

st.markdown(f"""
<style>
    .metric-card {{
        background-color: {config.COLOR_BACKGROUND};
        border-left: 5px solid {config.COLOR_DEBT};
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
    }}
    .status-ok {{ color: {config.COLOR_HEALTHY}; font-weight: bold; }}
    .status-debt {{ color: {config.COLOR_DEBT}; font-weight: bold; }}
    .health-score {{ font-size: 28px; font-weight: bold; text-align: center; }}
    .quick-win {{ background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin: 5px 0; }}
    h1, h2, h3 {{ font-family: 'Segoe UI', sans-serif; }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# 2. DATA GENERATION
# -----------------------------------------------
@st.cache_data
def generate_system_logs(n_rows: int = 1000, debt_ratio: float = 0.05) -> pd.DataFrame:
    """
    Generates synthetic backend logs with injected operational debt.
    """
    logger.info(f"Generating {n_rows} synthetic logs with {debt_ratio*100:.1f}% debt")
    
    data: list[dict[str, any]] = []
    base_time = datetime.now()
    
    for i in range(n_rows):
        ts = base_time - timedelta(seconds=i*2)
        endpoint = np.random.choice(config.SYNTHETIC_ENDPOINTS, p=config.ENDPOINT_DISTRIBUTION)
        is_debt = np.random.random() < debt_ratio
        
        if is_debt:
            latency = int(np.random.normal(config.DEBT_LATENCY_MEAN, config.DEBT_LATENCY_STD))
            status, log_type = 200, "Hidden Debt"
        else:
            latency = int(np.random.normal(config.HEALTHY_LATENCY_MEAN, config.HEALTHY_LATENCY_STD))
            if np.random.random() < 0.01:
                status, log_type = 500, "Hard Error"
            else:
                status, log_type = 200, "Healthy"
        
        latency = max(config.MIN_LATENCY, latency)
        data.append({
            'Timestamp': ts,
            'Endpoint': endpoint,
            'Latency_ms': latency,
            'Status': status,
            'True_Label': log_type
        })
    
    logger.info(f"Generated {len(data)} records")
    return pd.DataFrame(data).sort_values('Timestamp')

# -----------------------------------------------
# 3. MACHINE LEARNING
# -----------------------------------------------
def detect_operational_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """
    Uses Isolation Forest for unsupervised anomaly detection.
    """
    logger.info(f"Training Isolation Forest with contamination={contamination}")
    model = IsolationForest(contamination=contamination, random_state=config.ML_RANDOM_STATE)
    
    df['anomaly_score'] = model.fit_predict(df[['Latency_ms']])
    df['is_anomaly'] = df['anomaly_score'].map({1: False, -1: True})
    
    logger.info(f"Detected {df['is_anomaly'].sum()} anomalies")
    return df

# -----------------------------------------------
# 4. STRATEGY RECOMMENDATIONS
# -----------------------------------------------
def run_executive_agent_analysis(df_anomalies: pd.DataFrame) -> tuple[str, list[str]]:
    """Generate refactoring strategies for bottleneck endpoints."""
    if df_anomalies.empty:
        return "No significant debt detected.", []
    
    worst_endpoint = df_anomalies.groupby('Endpoint')['Latency_ms'].sum().idxmax()
    logger.info(f"Primary bottleneck: {worst_endpoint}")
    
    return get_strategy_for_endpoint(worst_endpoint)

# -----------------------------------------------
# 5. MAIN APP
# -----------------------------------------------
def main() -> None:
    # --- SIDEBAR ---
    st.sidebar.title("⚙️ OpsEx Control Plane")
    st.sidebar.markdown("**Configure Analysis Parameters**")
    
    # Data source
    data_source = st.sidebar.radio("📊 Data Source", ["Generate Synthetic", "Upload CSV"])
    
    if data_source == "Generate Synthetic":
        n_logs = st.sidebar.slider("Log Volume", 500, 5000, 1000)
        debt_ratio = st.sidebar.slider("Debt Injection (%)", 1, 20, 5) / 100
    else:
        uploaded_file = st.sidebar.file_uploader("Upload CSV (Timestamp, Endpoint, Latency_ms, Status)")
        debt_ratio = 0
    
    # ML Configuration
    contamination = st.sidebar.slider("ML Sensitivity", config.MIN_CONTAMINATION, config.MAX_CONTAMINATION, config.DEFAULT_CONTAMINATION)
    hourly_rate = st.sidebar.number_input("Engineer Cost/Hour ($)", value=config.DEFAULT_HOURLY_RATE, min_value=config.MIN_HOURLY_RATE)
    
    # SLA Template
    sla_level = st.sidebar.selectbox("SLA Template", ["aggressive", "standard", "relaxed"])
    
    # Alert Thresholds
    with st.sidebar.expander("⚠️ Alert Thresholds"):
        wasted_hours_threshold = st.number_input("Wasted hours alert >", value=config.DEFAULT_WASTED_HOURS_THRESHOLD)
        error_rate_threshold = st.number_input("Error rate alert > (%)", value=config.DEFAULT_ERROR_RATE_THRESHOLD)
    
    run_button = st.sidebar.button("🚀 Run Scanner", type="primary")
    if run_button:
        st.session_state['run_analysis'] = True
    
    st.sidebar.divider()
    st.sidebar.info("**Silent Debt**: High latency on 200 OK responses. It burns money silently.")

    # --- HEADER ---
    st.title("🛡️ Automated Operational Debt Scanner v2.0")
    st.markdown("**Detect → Quantify → Refactor**")
    st.markdown("Unsupervised ML identifies performance degradation hidden from error monitoring.")

    # --- ANALYSIS ---
    if st.session_state.get('run_analysis'):
        with st.spinner("⏳ Ingesting logs & analyzing..."):
            
            # Load data
            if data_source == "Generate Synthetic":
                raw_df = generate_system_logs(n_rows=n_logs, debt_ratio=debt_ratio)
            else:
                if not uploaded_file:
                    st.error("❌ Please upload a CSV file")
                    return
                raw_df = pd.read_csv(uploaded_file)
                raw_df['Timestamp'] = pd.to_datetime(raw_df['Timestamp'])
                
                # Validate
                is_valid, msg = validate_csv(raw_df)
                if not is_valid:
                    st.error(f"❌ {msg}")
                    return
                st.success(msg)
                
                raw_df = clean_data(raw_df)
            
            # ML
            processed_df = detect_operational_anomalies(raw_df.copy(), contamination)
            
            # Calculations
            anomalies = processed_df[processed_df['is_anomaly'] == True]
            normal = processed_df[processed_df['is_anomaly'] == False]
            baseline_latency = normal['Latency_ms'].mean() if not normal.empty else processed_df['Latency_ms'].quantile(0.25)
            
            anomalies_calc = anomalies.copy()
            anomalies_calc['Wasted_ms'] = (anomalies_calc['Latency_ms'] - baseline_latency).clip(lower=0)
            total_wasted_hours = anomalies_calc['Wasted_ms'].sum() / (1000 * 60 * 60)
            financial_loss = total_wasted_hours * hourly_rate
            error_rate = (processed_df['Status'] == 500).sum() / len(processed_df) * 100
            
            # Advanced metrics
            percentiles = calculate_percentiles(processed_df)
            trends = calculate_latency_trends(processed_df)
            peak_hours = find_peak_hours(processed_df)
            sla_compliance = calculate_sla_compliance(processed_df)
            health_score_data = generate_health_score(error_rate, sla_compliance['compliance_rate'], trends['slope'])

        # --- DASHBOARD ROW 1: KPIs ---
        st.divider()
        st.subheader("📊 Executive Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Requests", f"{len(processed_df):,}")
        with col2:
            st.metric("Anomalies Detected", f"{len(anomalies)}", f"{len(anomalies)/len(processed_df):.1%}")
        with col3:
            st.metric("Wasted Eng. Hours", f"{total_wasted_hours:.1f}h", f"${financial_loss:,.0f}")
        with col4:
            st.metric("Error Rate", f"{error_rate:.2f}%")
        with col5:
            health_color = "🟢" if health_score_data['health_score'] >= 80 else "🟡" if health_score_data['health_score'] >= 60 else "🔴"
            st.metric("Health Score", f"{health_color} {health_score_data['health_score']}", health_score_data['health_status'])
        
        # Alerts
        alert_cols = st.columns(2)
        with alert_cols[0]:
            if total_wasted_hours > wasted_hours_threshold:
                st.warning(f"⚠️ Wasted hours ({total_wasted_hours:.1f}h) exceed threshold ({wasted_hours_threshold:.1f}h)")
        with alert_cols[1]:
            if error_rate > error_rate_threshold:
                st.error(f"🔴 Error rate ({error_rate:.2f}%) exceeds threshold ({error_rate_threshold:.1f}%)")

        # --- DASHBOARD ROW 2: Visualizations ---
        st.divider()
        st.subheader("📈 Analytics")
        
        # Latency over time
        fig_scatter = px.scatter(
            processed_df,
            x="Timestamp", y="Latency_ms", color="is_anomaly",
            color_discrete_map={False: config.COLOR_HEALTHY, True: config.COLOR_DEBT},
            hover_data=['Endpoint', 'Status'],
            title="Latency Timeline (Red = Anomalies)"
        )
        fig_scatter.add_hline(y=baseline_latency, line_dash="dash", line_color=config.COLOR_BASELINE,
                             annotation_text=f"Baseline: {baseline_latency:.0f}ms")
        fig_scatter.update_layout(height=config.CHART_HEIGHT)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Per-endpoint metrics
        col_ep1, col_ep2 = st.columns([1.3, 1])
        with col_ep1:
            endpoint_metrics = calculate_endpoint_metrics(processed_df)
            endpoint_metrics_sorted = endpoint_metrics.sort_values('Mean_Latency', ascending=False)
            
            fig_ep = px.bar(
                endpoint_metrics_sorted,
                x='Endpoint', y='Mean_Latency', color='Error_Rate',
                color_continuous_scale='RdYlGn_r',
                title='Mean Latency by Endpoint',
                hover_data=['Total_Requests', 'Error_Rate', 'Std_Dev']
            )
            st.plotly_chart(fig_ep, use_container_width=True)
        
        with col_ep2:
            st.markdown("**Endpoint Metrics**")
            st.dataframe(
                endpoint_metrics_sorted[['Endpoint', 'Mean_Latency', 'Error_Rate', 'Total_Requests', 'Std_Dev']].head(10),
                use_container_width=True, hide_index=True
            )
        
        # Percentiles & SLA Compliance
        col_perc1, col_perc2 = st.columns(2)
        with col_perc1:
            st.markdown("**Latency Percentiles**")
            perc_col1, perc_col2, perc_col3, perc_col4 = st.columns(4)
            with perc_col1:
                st.metric("P50", f"{percentiles['P50']:.0f}ms")
            with perc_col2:
                st.metric("P75", f"{percentiles['P75']:.0f}ms")
            with perc_col3:
                st.metric("P95", f"{percentiles['P95']:.0f}ms")
            with perc_col4:
                st.metric("P99", f"{percentiles['P99']:.0f}ms")
        
        with col_perc2:
            st.markdown("**SLA Compliance**")
            sla_eval = evaluate_against_sla(percentiles, sla_level)
            sla_cols = st.columns(3)
            with sla_cols[0]:
                status = "✅" if sla_eval['p95_compliant'] else "❌"
                st.metric("P95 SLA", status)
            with sla_cols[1]:
                status = "✅" if sla_eval['p99_compliant'] else "❌"
                st.metric("P99 SLA", status)
            with sla_cols[2]:
                st.caption(f"Template: {sla_level}")

        # --- DASHBOARD ROW 3: Intelligence ---
        st.divider()
        st.subheader("🤖 AI Recommendations")
        
        col_strat, col_data = st.columns([1, 1])
        
        with col_strat:
            st.markdown("**Refactoring Strategy**")
            worst_ep, steps = run_executive_agent_analysis(anomalies_calc)
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>🛑 Primary Bottleneck: <code>{worst_ep}</code></h4>
                <p>This endpoint contributes {(anomalies_calc[anomalies_calc['Endpoint']==worst_ep]['Latency_ms'].sum()/anomalies_calc['Latency_ms'].sum()*100):.1f}% of total latency debt.</p>
            </div>
            """, unsafe_allow_html=True)
            
            for i, step in enumerate(steps, 1):
                st.markdown(f"**{i}.** {step}")
            
            # ROI
            st.markdown("**💰 Savings Potential**")
            roi_data = calculate_roi_potential(anomalies_calc, baseline_latency, hourly_rate)
            for endpoint, metrics in sorted(roi_data.items(), key=lambda x: x[1]['potential_savings'], reverse=True)[:3]:
                st.metric(endpoint, f"${metrics['potential_savings']:,.0f}", f"{metrics['wasted_hours']:.1f}h wasted")
        
        with col_data:
            st.markdown("**Quick Wins**")
            for win in get_quick_wins(len(anomalies), financial_loss)[:4]:
                st.markdown(f'<div class="quick-win">{win}</div>', unsafe_allow_html=True)
            
            st.markdown("**Trend Analysis**")
            st.info(f"🔄 {trends['trend']} (slope: {trends['slope']:.2f} ms/hour)")
            st.info(f"⏰ **Peak Hour**: {peak_hours['peak_hour']} ({peak_hours['peak_latency']:.0f}ms avg)")

        # --- DASHBOARD ROW 4: Data Export ---
        st.divider()
        st.subheader("📥 Export & Details")
        
        exp_cols = st.columns(3)
        
        with exp_cols[0]:
            csv_buffer = io.StringIO()
            anomalies_calc[['Timestamp', 'Endpoint', 'Latency_ms', 'Wasted_ms', 'Status']].to_csv(csv_buffer, index=False)
            st.download_button(
                label="📊 Download Anomalies (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"opex_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with exp_cols[1]:
            st.write("---")
        
        with exp_cols[2]:
            st.caption(f"Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Severity distribution
        st.markdown("**Anomaly Severity**")
        anomalies_severity = calculate_anomaly_severity(anomalies_calc, baseline_latency)
        fig_sev = go.Figure(data=[
            go.Histogram(x=anomalies_severity['Severity_Score'], nbinsx=20, marker_color=config.COLOR_DEBT, name='Severity')
        ])
        fig_sev.update_layout(title='Severity Score Distribution', xaxis_title='Score (0-100)', yaxis_title='Count', height=300)
        st.plotly_chart(fig_sev, use_container_width=True)

    else:
        # Landing page
        st.info("👈 Configure parameters and click **Run Scanner** to analyze system performance.")
        
        st.markdown("---")
        st.markdown("### ✨ Features")
        st.markdown("""
        - **CSV Upload**: Analyze real production logs
        - **SLA Templates**: Aggressive/Standard/Relaxed monitoring
        - **Percentiles**: P50/P75/P95/P99 tracking
        - **Health Score**: Composite system health metric
        - **Trend Detection**: Is latency improving or degrading?
        - **Peak Hour Analysis**: When does system perform worst?
        - **ROI Calculations**: Cost-benefit for each fix
        - **Multi-Pattern Strategies**: 8+ endpoint types supported
        - **Quick Wins**: Actionable optimization suggestions
        """)
        
        st.markdown("---")
        st.code("""
# OpsEx Debt Scanner v2.0
model = IsolationForest(contamination=0.05)
anomalies = detect_operational_anomalies(df)
roi = calculate_savings_per_endpoint(anomalies)
health_score = generate_health_score(error_rate, sla_comp, trend)
        """, language="python")

if __name__ == "__main__":
    main()
