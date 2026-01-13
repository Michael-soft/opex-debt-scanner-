# Input validation utilities

import pandas as pd


def validate_csv(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate uploaded CSV structure and content.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check for empty dataset
    if df.empty:
        return False, "❌ Empty dataset provided"
    
    # Check required columns
    required_cols = {'Timestamp', 'Endpoint', 'Latency_ms', 'Status'}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        return False, f"❌ Missing columns: {', '.join(missing_cols)}"
    
    # Validate data types
    if not pd.api.types.is_numeric_dtype(df['Latency_ms']):
        return False, "❌ Latency_ms must be numeric"
    
    if not pd.api.types.is_numeric_dtype(df['Status']):
        return False, "❌ Status must be numeric"
    
    # Check for negative latencies
    if (df['Latency_ms'] < 0).any():
        return False, "❌ Latency cannot be negative"
    
    # Check for reasonable status codes
    if not df['Status'].isin(range(100, 600)).all():
        return False, "❌ Invalid HTTP status codes (must be 100-599)"
    
    # Check for endpoints
    if df['Endpoint'].isna().any():
        return False, "❌ Missing endpoint names"
    
    # Check for timestamps
    try:
        pd.to_datetime(df['Timestamp'])
    except:
        return False, "❌ Invalid timestamp format (try YYYY-MM-DD HH:MM:SS)"
    
    # Warnings for unusual data (but still valid)
    if df['Latency_ms'].max() > 30000:
        pass  # Warn about extremely high latencies
    
    return True, f"✅ Valid dataset: {len(df)} records"


def clean_data(df: pd.DataFrame, cap_outliers: bool = True) -> pd.DataFrame:
    """
    Clean and prepare data for analysis.
    
    Args:
        df: Input DataFrame
        cap_outliers: Whether to cap extreme outliers at 99th percentile
        
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Remove null values
    df = df.dropna(subset=['Latency_ms', 'Status', 'Endpoint'])
    
    # Convert timestamp to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Cap extreme outliers at 99th percentile
    if cap_outliers:
        q99 = df['Latency_ms'].quantile(0.99)
        df['Latency_ms'] = df['Latency_ms'].clip(upper=q99)
    
    # Ensure positive latencies
    df['Latency_ms'] = df['Latency_ms'].clip(lower=10)
    
    return df


def validate_parameters(
    contamination: float,
    hourly_rate: float,
    wasted_hours_threshold: float,
    error_rate_threshold: float
) -> tuple[bool, str]:
    """
    Validate user-provided parameters.
    
    Args:
        contamination: ML contamination parameter
        hourly_rate: Engineering cost per hour
        wasted_hours_threshold: Alert threshold for wasted hours
        error_rate_threshold: Alert threshold for error rate
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not (0.01 <= contamination <= 0.15):
        return False, "Contamination must be between 0.01 and 0.15"
    
    if hourly_rate < 10:
        return False, "Hourly rate must be at least $10"
    
    if wasted_hours_threshold < 0:
        return False, "Wasted hours threshold must be positive"
    
    if not (0 <= error_rate_threshold <= 100):
        return False, "Error rate threshold must be between 0 and 100%"
    
    return True, "Valid parameters"
