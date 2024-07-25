from rest_framework import serializers
from .models import *

class CreateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'photo', 'address', 'open_time', 'close_time', 'tel', 'latitude', 'longitude', 'type']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'