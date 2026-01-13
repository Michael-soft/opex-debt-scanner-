# Analytics and metrics calculation utilities

import pandas as pd
import numpy as np
from config import PERCENTILES


def calculate_endpoint_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive per-endpoint metrics.
    
    Args:
        df: Input DataFrame with Endpoint, Latency_ms, Status columns
        
    Returns:
        DataFrame with aggregated metrics per endpoint
    """
    metrics = df.groupby('Endpoint').agg({
        'Latency_ms': ['mean', 'median', 'std', 'min', 'max', 'count'],
        'Status': lambda x: (x >= 500).sum()  # Captures all 5xx errors: 500, 502, 503, 504, etc.
    }).round(2)
    
    metrics.columns = ['Mean_Latency', 'Median_Latency', 'Std_Dev',
                       'Min_Latency', 'Max_Latency', 'Total_Requests', 'Error_Count']
    metrics['Error_Rate'] = (metrics['Error_Count'] / metrics['Total_Requests'] * 100).round(2)
    
    return metrics.reset_index()


def calculate_percentiles(df: pd.DataFrame, endpoint: str = None) -> dict[str, float]:
    """
    Calculate SLA-relevant percentiles (P50, P75, P95, P99).
    
    Args:
        df: Input DataFrame
        endpoint: Optional endpoint to filter (if None, uses all data)
        
    Returns:
        Dictionary mapping percentile names to values
    """
    if endpoint:
        data = df[df['Endpoint'] == endpoint]['Latency_ms']
    else:
        data = df['Latency_ms']
    
    return {
        f'P50': round(data.quantile(0.50), 2),
        'P75': round(data.quantile(0.75), 2),
        'P95': round(data.quantile(0.95), 2),
        'P99': round(data.quantile(0.99), 2),
    }


def calculate_anomaly_severity(anomalies: pd.DataFrame, baseline: float) -> pd.DataFrame:
    """
    Calculate severity score for each anomaly (0-100 scale).
    
    Args:
        anomalies: DataFrame of anomalous records
        baseline: Baseline latency in milliseconds
        
    Returns:
        DataFrame with Severity_Score column added
    """
    anomalies_copy = anomalies.copy()
    anomalies_copy['Severity_Score'] = (
        ((anomalies_copy['Latency_ms'] - baseline) / max(baseline, 1) * 100)
        .clip(0, 100)
        .round(1)
    )
    return anomalies_copy


def calculate_roi_potential(
    anomalies: pd.DataFrame,
    baseline: float,
    hourly_rate: float
) -> dict[str, dict[str, float]]:
    """
    Calculate potential ROI of fixing performance bottlenecks by endpoint.
    
    Args:
        anomalies: DataFrame of anomalous records
        baseline: Baseline latency in milliseconds
        hourly_rate: Engineer cost per hour in USD
        
    Returns:
        Dictionary mapping endpoint to {'wasted_hours': float, 'potential_savings': float}
    """
    roi_data = {}
    
    for endpoint in anomalies['Endpoint'].unique():
        endpoint_anomalies = anomalies[anomalies['Endpoint'] == endpoint]
        wasted_ms = (endpoint_anomalies['Latency_ms'] - baseline).sum()
        wasted_hours = wasted_ms / (1000 * 60 * 60)
        potential_savings = wasted_hours * hourly_rate
        
        roi_data[endpoint] = {
            'wasted_hours': round(wasted_hours, 2),
            'potential_savings': round(potential_savings, 2),
            'anomaly_count': len(endpoint_anomalies)
        }
    
    return roi_data


def calculate_latency_trends(df: pd.DataFrame) -> dict:
    """
    Detect if latency is improving or degrading over time.
    
    Args:
        df: Input DataFrame with Timestamp and Latency_ms columns
        
    Returns:
        Dictionary with trend direction and slope
    """
    if len(df) < 2:
        return {'trend': 'Insufficient data', 'slope': 0}
    
    df = df.copy()
    df['hour'] = df['Timestamp'].dt.floor('H')
    hourly_latency = df.groupby('hour')['Latency_ms'].mean()
    
    if len(hourly_latency) < 2:
        return {'trend': 'Insufficient data', 'slope': 0}
    
    # Calculate slope (positive = degrading, negative = improving)
    x = np.arange(len(hourly_latency))
    y = hourly_latency.values
    slope = np.polyfit(x, y, 1)[0]
    
    trend = 'Degrading ⬆️' if slope > 5 else ('Improving ⬇️' if slope < -5 else 'Stable ➡️')
    
    return {
        'trend': trend,
        'slope': round(slope, 2),
        'direction': 'worse' if slope > 0 else 'better'
    }


def find_peak_hours(df: pd.DataFrame) -> dict[str, any]:
    """
    Identify when system performs worst (peak latency hours).
    
    Args:
        df: Input DataFrame with Timestamp and Latency_ms columns
        
    Returns:
        Dictionary with peak hour and metrics
    """
    df = df.copy()
    df['hour'] = df['Timestamp'].dt.hour
    
    hourly_stats = df.groupby('hour')['Latency_ms'].agg(['mean', 'max', 'count']).round(2)
    peak_hour = hourly_stats['mean'].idxmax()
    
    return {
        'peak_hour': f"{peak_hour:02d}:00",
        'peak_latency': hourly_stats.loc[peak_hour, 'mean'],
        'peak_requests': int(hourly_stats.loc[peak_hour, 'count'])
    }


def calculate_sla_compliance(df: pd.DataFrame, sla_latency_ms: float = 500) -> dict:
    """
    Calculate SLA compliance percentage based on latency threshold.
    
    Args:
        df: Input DataFrame with Latency_ms column
        sla_latency_ms: SLA threshold in milliseconds
        
    Returns:
        Dictionary with compliance metrics
    """
    total = len(df)
    compliant = (df['Latency_ms'] <= sla_latency_ms).sum()
    
    return {
        'sla_threshold_ms': sla_latency_ms,
        'compliance_rate': round(compliant / total * 100, 2),
        'non_compliant_count': total - compliant
    }


def generate_health_score(
    error_rate: float,
    compliance_rate: float,
    trend_slope: float
) -> dict[str, any]:
    """
    Generate overall system health score (0-100).
    
    Args:
        error_rate: Error rate percentage
        compliance_rate: SLA compliance percentage
        trend_slope: Latency trend slope
        
    Returns:
        Dictionary with health score and breakdown
    """
    # Components weighted equally
    error_score = max(0, 100 - error_rate * 2)  # 0.5% per error point
    compliance_score = compliance_rate  # Direct percentage
    trend_score = max(0, 100 - (abs(trend_slope) * 0.5))  # Penalize bad trends
    
    overall_score = round((error_score + compliance_score + trend_score) / 3, 1)
    
    health = 'Excellent 🟢' if overall_score >= 80 else \
             'Good 🟡' if overall_score >= 60 else \
             'Poor 🔴'
    
    return {
        'health_score': overall_score,
        'health_status': health,
        'error_score': round(error_score, 1),
        'compliance_score': round(compliance_score, 1),
        'trend_score': round(trend_score, 1)
    }
