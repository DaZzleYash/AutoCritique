from core.models import Signal, RiskAssessment

def assess_risk(workflow):
    signals = Signal.objects.filter(step_execution__step__workflow=workflow)
    risk_score = 0
    if not signals.exists():
        return RiskAssessment.objects.create(
            workflow=workflow,
            risk_score=0,
            summary="No significant risk detected."
        )
    else:
        recent_ten_signals = signals.order_by('-created_at')[:10]
        retry_spike, latency_spike = 0, 0
        for signal in recent_ten_signals:
            if signal.signal_type == 'retry_spike':
                retry_spike+=1
                risk_score+=(signal.signal_scale*3)
            elif signal.signal_type == 'latency_spike':
                latency_spike+=1
                risk_score+=(signal.signal_scale*2)
        risk_score = min(100, risk_score)
        summary = None
        if retry_spike>latency_spike:
            summary = "Frequent retry spikes detected. System stability is degrading."
        elif retry_spike<latency_spike:
            summary = "Frequent latency spikes detected. System stability is degrading."
        else:
            summary = "Frequent retry spikes and latency spikes are detected. System stability is degrading."
        RiskAssessment.objects.create(
            workflow=workflow, 
            risk_score = risk_score, 
            summary = summary
        )
