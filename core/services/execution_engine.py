from core.models import *
from django.utils import timezone
from .step_handler import step_handler
from .signal_detection import detect_signals
from .risk_engine import assess_risk

def create_execution(workflow_id, execution_mode):
    workflow = Workflow.objects.get(pk=workflow_id)
    execution = Execution.objects.create(
        workflow = workflow, 
        started_at = timezone.now(), 
        execution_mode=execution_mode
    )
    return execution

def finalize_execution(workflow_execution, failed_occoured, any_success):
    workflow_execution.ended_at = timezone.now()
    if not any_success:
        workflow_execution.status = 'failed'
    elif failed_occoured:
        workflow_execution.status = 'partial'
    else:
        workflow_execution.status = 'success'
    workflow_execution.save()
    return workflow_execution

def execute_workflow(workflow_id, execution_mode):

    wf_execution = create_execution(workflow_id, execution_mode)
    
    steps = wf_execution.workflow.steps.all()

    # For no steps execution
    if not steps.exists():
        wf_execution.ended_at = timezone.now()
        wf_execution.status = 'success'
        wf_execution.save()
        return  wf_execution
    
    # Set first step as the first step won't always be 1
    failed_occurred = False
    any_success = False
    for step in steps:
        # retry system considering max of 3 re-tries.
        available_retries = 3
        attempt = 0
        while attempt <= available_retries:

            step_result = step_handler(step)
            print(step_result)

            if step_result['status'] == 'success':
                break

            if not step_result.get('retryable', False):
                break

            if attempt == available_retries:
                break

            attempt += 1

        step_execution = StepExecution.objects.create(
            execution = wf_execution, 
            step = step, 
            status = step_result['status'], 
            duration = step_result['duration'], 
            retry_count = attempt, 
            output_characteristics = step_result['output_characteristics']
        )

        #signals
        detect_signals(step_execution)

        # handle failed step
        if step_execution.status.lower() == 'failed':
            failed_occurred = True
            break
        any_success = True

    execution = finalize_execution(wf_execution, failed_occurred, any_success)

    assess_risk(execution.workflow)

    return execution
