from celery import shared_task
from .services.execution_engine import execute_workflow
import logging

logger = logging.getLogger(__name__)

@shared_task
def execute_workflow_async(workflow_id, execution_mode):
    try:
        execution = execute_workflow(workflow_id, execution_mode)
        # Return only serializable data
        return {
            "id": execution.id,
            "workflow_id": execution.workflow.id,
            "status": execution.status,
            "started_at": str(execution.started_at),
            "ended_at": str(execution.ended_at),
            "execution_mode": execution.execution_mode,
        }
    except Exception as e:
        logger.exception(f"Error in execute_workflow_async: {e}")
        return {"error": str(e)}
