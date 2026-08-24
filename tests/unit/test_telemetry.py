from src.core.telemetry import MetricsCollector


def test_telemetry_aggregates_latency_tokens_and_cost():
    collector = MetricsCollector()
    collector.record_request(12.5)
    collector.record_request(7.5)
    collector.record_llm_call(prompt_tokens=10, completion_tokens=5, cost_usd=0.000006)

    result = collector.summary()

    assert result.requests == 2
    assert result.total_latency_ms == 20.0
    assert result.llm_calls == 1
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert result.estimated_cost_usd == 0.000006
