from core.models import StepExecution, Signal

def detect_signals(step_execution):
    step = step_execution.step
    step_execution_history = StepExecution.objects.filter(step=step).exclude(id=step_execution.id)
    if step_execution_history.count() < 3:
        return None
    
    # in reverse order and last 5(excluding current)
    last_five_instances = list(step_execution_history.order_by('-created_at'))[:5]
    last_five_instances_duration = []
    last_five_retry_count = []
    for i in last_five_instances:
        last_five_instances_duration.append(i.duration)
        last_five_retry_count.append(i.retry_count)
    avg_duration = (sum(last_five_instances_duration))/len(last_five_instances_duration)
    avg_retry = (sum(last_five_retry_count))/len(last_five_retry_count)
    current_retry = step_execution.retry_count
    current_duration = step_execution.duration

    if current_duration>(avg_duration*2):
        if avg_duration > 0:
            ratio = current_duration/avg_duration
        else:
            ratio = current_duration
        scale = min(10, int(ratio))

        Signal.objects.create(
            step_execution = step_execution, 
            signal_scale = scale, 
            signal_type = 'latency_spike', 
            detected_value = current_duration, 
            baseline_value = avg_duration
        )

    if current_retry>(avg_retry+2):
        if avg_retry > 0:
            ratio = current_retry/avg_retry
        else:
            ratio = current_retry
        scale = min(10, int(ratio))

        Signal.objects.create(
            step_execution = step_execution, 
            signal_scale = scale, 
            signal_type = 'retry_spike', 
            detected_value = current_retry, 
            baseline_value = avg_retry
        )

