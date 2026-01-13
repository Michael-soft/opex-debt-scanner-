# Refactoring strategy recommendations engine


# Comprehensive strategy patterns for various endpoint types
STRATEGY_PATTERNS: dict[str, dict[str, str]] = {
    "search|query": {
        "immediate": "Implement Redis/Memcached layer for query results caching",
        "root_cause": "ElasticSearch indices unoptimized, missing shards, or network latency",
        "long_term": "Migrate to event-driven CQRS pattern with projection layer"
    },
    "report|export": {
        "immediate": "Move to async job queue (Celery/Bull/RQ) to unblock HTTP threads",
        "root_cause": "Large dataset aggregation blocking request, slow aggregation pipeline",
        "long_term": "Implement materialized views or data warehouse with hourly refreshes"
    },
    "transaction|payment|checkout": {
        "immediate": "Add timeout handling and implement retry logic with exponential backoff",
        "root_cause": "External payment processor delays, network issues, or unoptimized database queries",
        "long_term": "Isolate transaction processing into dedicated microservice with circuit breakers"
    },
    "auth|login|oauth|jwt": {
        "immediate": "Implement token caching with short TTL (Redis)",
        "root_cause": "Identity provider latency or excessive permission checks (N+1 queries)",
        "long_term": "Adopt passwordless authentication (WebAuthn) or federation"
    },
    "upload|file|media": {
        "immediate": "Stream uploads directly to S3/Cloud Storage; validate client-side",
        "root_cause": "Processing files before persisting to storage, or single-threaded uploads",
        "long_term": "Implement chunked multi-part uploads with resumable progress tracking"
    },
    "profile|user|account": {
        "immediate": "Cache user profiles in distributed cache (Redis) with 5-min TTL",
        "root_cause": "Repeated database lookups for profile data, unindexed queries",
        "long_term": "Implement event-sourced user projections with eventual consistency"
    },
    "notification|email|sms": {
        "immediate": "Move to message queue (RabbitMQ/Kafka) for async processing",
        "root_cause": "Blocking HTTP waits for notification delivery",
        "long_term": "Implement event-driven notification system with retry queues"
    },
    "database|sql": {
        "immediate": "Add query result caching and implement connection pooling",
        "root_cause": "Missing database indexes, connection pool exhaustion, or slow queries",
        "long_term": "Shard database, implement read replicas, or migrate to NoSQL where appropriate"
    },
}


def get_strategy_for_endpoint(worst_endpoint: str) -> tuple[str, list[str]]:
    """
    Generate refactoring strategies for an endpoint.
    
    Args:
        worst_endpoint: The endpoint path (e.g., '/api/v1/search/query')
        
    Returns:
        Tuple of (endpoint, [immediate, root_cause, long_term] strategies)
    """
    # Normalize endpoint for matching
    endpoint_lower = worst_endpoint.lower()
    
    # Try to match against patterns
    for pattern, strategies in STRATEGY_PATTERNS.items():
        keywords = pattern.split('|')
        if any(keyword in endpoint_lower for keyword in keywords):
            plan = [
                f"**⚡ Immediate Mitigation:** {strategies['immediate']}",
                f"**🔍 Root Cause Analysis:** {strategies['root_cause']}",
                f"**🚀 Long Term Strategy:** {strategies['long_term']}"
            ]
            return worst_endpoint, plan
    
    # Default/fallback strategy
    plan = [
        f"**⚡ Immediate Mitigation:** Review application logs for `{worst_endpoint}` during high-latency windows. Add detailed APM instrumentation.",
        "**🔍 Root Cause Analysis:** Check CPU/memory saturation on host nodes. Verify connection pool exhaustion (increase max_pool_size or implement PgBouncer).",
        f"**🚀 Long Term Strategy:** Profile `{worst_endpoint}` with flame graphs. Consider horizontal scaling or request queuing."
    ]
    return worst_endpoint, plan


def get_quick_wins(anomalies_count: int, financial_loss: float) -> list[str]:
    """
    Suggest quick wins based on the severity of debt detected.
    
    Args:
        anomalies_count: Number of detected anomalies
        financial_loss: Estimated financial impact in dollars
        
    Returns:
        List of actionable quick win suggestions
    """
    quick_wins = []
    
    if anomalies_count > 100:
        quick_wins.append("🎯 **High Priority**: Implement basic caching layer (Redis) - Quick win with 40-60% latency reduction")
    
    if financial_loss > 500:
        quick_wins.append(f"💰 **ROI Alert**: ${financial_loss:.0f} cost/day - Justifies hiring/outsourcing for optimization")
    
    if anomalies_count > 500:
        quick_wins.append("⚠️ **Critical**: Consider load balancing, horizontal scaling, or circuit breaker patterns")
    
    quick_wins.append("✅ **Easy Win**: Add request-level caching (HTTP headers, ETag) for GET endpoints")
    quick_wins.append("✅ **Quick Fix**: Implement database query result caching (short TTL)")
    quick_wins.append("✅ **Infrastructure**: Verify connection pools are sized correctly for your workload")
    
    return quick_wins


def get_maturity_level_advice(mean_latency: float) -> str:
    """
    Provide optimization maturity advice based on current latency.
    
    Args:
        mean_latency: Mean latency in milliseconds
        
    Returns:
        Advice string with maturity level
    """
    if mean_latency < 50:
        return "🌟 **World-Class**: Your systems are highly optimized. Focus on maintaining SLAs and preventing regressions."
    elif mean_latency < 100:
        return "✅ **Production-Ready**: Good baseline performance. Continue monitoring and optimize outliers."
    elif mean_latency < 300:
        return "⚠️ **Needs Work**: Consider caching and query optimization. User experience is at risk."
    elif mean_latency < 1000:
        return "🔴 **Critical**: Immediate optimization needed. Users experiencing significant delays. Implement caching + async processing."
    else:
        return "🚨 **Emergency**: System is severely degraded. Implement circuit breakers and fallbacks immediately."


# SLA Templates
SLA_TEMPLATES = {
    "aggressive": {
        "p50": 100,
        "p95": 250,
        "p99": 500,
        "description": "High-performance, low-latency systems (e.g., real-time trading, live gaming)"
    },
    "standard": {
        "p50": 200,
        "p95": 500,
        "p99": 1000,
        "description": "Typical web applications and APIs"
    },
    "relaxed": {
        "p50": 500,
        "p95": 2000,
        "p99": 5000,
        "description": "Background jobs, batch processing, non-critical systems"
    }
}


def evaluate_against_sla(percentiles: dict, sla_level: str = "standard") -> dict:
    """
    Evaluate performance against SLA templates.
    
    Args:
        percentiles: Dictionary with P50, P95, P99 values
        sla_level: One of 'aggressive', 'standard', 'relaxed'
        
    Returns:
        Dictionary with SLA compliance assessment
    """
    sla = SLA_TEMPLATES.get(sla_level, SLA_TEMPLATES["standard"])
    
    results = {
        'p50_compliant': percentiles.get('P50', 0) <= sla['p50'],
        'p95_compliant': percentiles.get('P95', 0) <= sla['p95'],
        'p99_compliant': percentiles.get('P99', 0) <= sla['p99'],
        'sla_level': sla_level,
        'sla_description': sla['description']
    }
    
    results['all_compliant'] = all([results['p50_compliant'], results['p95_compliant'], results['p99_compliant']])
    
    return results
