from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import WorkFlowSerializer, StepSerializer, RiskAssessmentSerializer
from .models import *
from django.shortcuts import get_object_or_404
from .services.execution_engine import execute_workflow
from .services.risk_engine import assess_risk
from .tasks import execute_workflow_async

class WorkFlowCreateOrListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owner = self.request.user
        serializer = WorkFlowSerializer(Workflow.objects.filter(owner=owner), many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WorkFlowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response({"Msg":"create"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkflowDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"No data found"}, status=status.HTTP_404_NOT_FOUND)
        if workflow.owner == request.user:
            serializer = WorkFlowSerializer(workflow)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"Msg":"You don't own this workflow"}, status=status.HTTP_403_FORBIDDEN)
        
    def put(self, request, pk):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"No data found"}, status=status.HTTP_404_NOT_FOUND)
        if workflow.owner == request.user:
            serializer = WorkFlowSerializer(workflow, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Msg":"You do not own this workflow. Hence, step updation is unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, pk):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"No data Found"}, status=status.HTTP_404_NOT_FOUND)
        workflow.delete()
        return Response({"Msg":f"deleted object with id: {pk}"}, status=status.HTTP_204_NO_CONTENT)

class StepsCreateOrListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"No workflow found"}, status=status.HTTP_404_NOT_FOUND)
        steps = Step.objects.filter(workflow=workflow)
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, pk):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"No workflow Found"}, status=status.HTTP_404_NOT_FOUND)
        if workflow.owner == request.user:
            serializer = StepSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(workflow=workflow)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Msg":"You do not own this workflow. Hence, step creation is unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
class StepUpdateOrDelete(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            step = Step.objects.get(pk=pk)
            workflow = step.workflow
        except Step.DoesNotExist:
            return Response({"Msg":"Step doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        if workflow.owner == request.user:
            serializer = StepSerializer(step, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"Msg":"You do not own this workflow. Hence, step updation is unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        try: 
            step = Step.objects.get(pk=pk)
            workflow = step.workflow
        except Step.DoesNotExist:
            return Response({"Msg":"Step does't exists"})
        if workflow.owner == request.user:
            step.delete()
            return Response({"Msg":f"deleted object with id: {pk}"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Msg":"You do not own this workflow. Hence, step deletion is unauthorized"}, status=status.HTTP_403_FORBIDDEN)

class TriggerWorkFlow(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        execution_mode = request.data.get('execution_mode', 'simulated')
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"Workflow does not exists"}, status=status.HTTP_404_NOT_FOUND)
        if workflow.owner == request.user:
            execute_workflow_async.delay(workflow.id, execution_mode)
            return Response({"Msg":f"Workflow execution started with workflow id {pk}"}, status=status.HTTP_200_OK)
        return Response({"Msg":"Only owner can trigger the workflow"}, status=status.HTTP_403_FORBIDDEN)

class RiskAssessmentAPI(APIView):

    def get(self, request, pk):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({"Msg":"Workflow doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        risk_details = RiskAssessment.objects.filter(workflow=workflow)
        serializer = RiskAssessmentSerializer(risk_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
