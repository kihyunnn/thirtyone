from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def create_store(request):
    serializer = CreateStoreSerializer(data=request.data)
    if serializer.is_valid():
        store = serializer.save()
        return Response({"message": "create store successful"}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def view_store(request): 
    store = get_object_or_404(Store, id=1)
    # store id 값 1로 고정해줌(파리바게트 인하대점)
    serializer = StoreSerializer(store)
    return Response(serializer.data, status=200)