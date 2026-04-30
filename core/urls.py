from django.contrib import admin
from django.urls import path
from .views import WorkFlowCreateOrListAPIView, WorkflowDetailAPIView, StepsCreateOrListAPIView, StepUpdateOrDelete, TriggerWorkFlow, RiskAssessmentAPI
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token-pair'), 
    path('workflows/', WorkFlowCreateOrListAPIView.as_view(), name='workflow'), 
    path('workflows/<int:pk>/', WorkflowDetailAPIView.as_view(), name='work-detail'), 
    path('workflows/<int:pk>/steps/', StepsCreateOrListAPIView.as_view()), 
    path('steps/<int:pk>/', StepUpdateOrDelete.as_view()), 
    path('workflows/<int:pk>/execute/', TriggerWorkFlow.as_view()), 
    path('workflows/<int:pk>/risk/', RiskAssessmentAPI.as_view())
]