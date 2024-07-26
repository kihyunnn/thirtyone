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

@api_view(['POST'])
def create_product(request, pk):
    store = get_object_or_404(Store, pk=pk)
    name = request.data.get(name=name)
    sale_product, created  = SaleProduct.objects.get_or_create(store=store, name=name)
    
    if created:
        serializer = CreateSaleProductSerializer(sale_product, data=request.data)
    else :
        serializer = CreateSaleProductSerializer(sale_product, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        if created:
            return Response({'message': 'Sale product created successfully.', 'data': serializer.data}, status=201)
        else:
            return Response({'message': 'Sale product updated successfully.', 'data': serializer.data}, status=200)
        
    return Response(serializer.errors, status=400)

