from rest_framework import serializers
from .models import employee_info, EmployeeImage

class EmployeeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = employee_info
        fields = '__all__'
        
class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = '__all__'

class ImageSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.URLField())