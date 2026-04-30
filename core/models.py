from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Workflow(models.Model):
    choices = [('manual', 'Manual'), ('scheduled', 'Scheduled')]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    trigger_type = models.TextField(choices=choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Step(models.Model):
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    order = models.PositiveIntegerField()
    step_type = models.CharField(max_length=100)
    step_config = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("workflow", "order")
        ordering = ["order"]

    def __str__(self):
        return f"Step {self.order} ({self.step_type})"

class Execution(models.Model):
    choices = [('success', 'Success'), ('partial', 'Partial'), ('failed', 'Failed')]
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=choices, max_length=100)
    execution_mode = models.CharField(choices=[('simulated', 'Simulated'), ('real', 'Real')], max_length=100)
    
    
class StepExecution(models.Model):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='step_executions')
    status = models.CharField(max_length=100)
    duration = models.PositiveIntegerField()
    retry_count = models.PositiveIntegerField()
    output_characteristics = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

class Signal(models.Model):
    step_execution = models.ForeignKey(StepExecution, on_delete=models.CASCADE, related_name='signals')
    signal_type = models.CharField(max_length=50)
    signal_scale = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    detected_value = models.PositiveIntegerField()
    baseline_value = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class RiskAssessment(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    risk_score = models.PositiveIntegerField()
    summary = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Insight(models.Model):
    risk = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE)
    insight = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
