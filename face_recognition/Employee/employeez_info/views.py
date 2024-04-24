from rest_framework import generics
from .models import employee_info, EmployeeImage, ImageModel
from .serializers import EmployeeInfoSerializer, EmployeeImageSerializer
from django.http import HttpResponse
from django.conf import settings
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ImageSerializer
import logging
from django.views import View

class EmployeeInfoListCreateAPIView(generics.ListCreateAPIView):
    queryset = employee_info.objects.all()
    serializer_class = EmployeeInfoSerializer

class EmployeeInfoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = employee_info.objects.all()
    serializer_class = EmployeeInfoSerializer

class EmployeeImageListCreateAPIView(generics.ListCreateAPIView):
    queryset = EmployeeImage.objects.all()
    serializer_class = EmployeeImageSerializer

class EmployeeImageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmployeeImage.objects.all()
    serializer_class = EmployeeImageSerializer


logger = logging.getLogger(__name__)

class ImageView(APIView):
    def get(self, request):
        # Retrieve all image instances from the database
        images = ImageModel.objects.all()

        # List to store image URLs
        image_urls = []

        # Generate URLs for each image instance
        for image in images:
            # Construct the image URL using the Django settings
            image_url = os.path.join(settings.MEDIA_URL, str(image.image))
            image_urls.append(image_url)

        serializer = ImageSerializer({'images': image_urls})  # Pass data to the serializer
        return Response(serializer.data)
# views.py

from django.http import JsonResponse
from .models import ImageModel


class LatestFramesView(View):
    def get(self, request):
        # Retrieve the latest frames from the database
        latest_frames = ImageModel.objects.order_by('-marked_time')[:10]  # Use the appropriate field here

        # Serialize the frames and format the image URLs
        serialized_frames = [{'image_url': frame.image.url.replace('\\', '/')} for frame in latest_frames]

        # Return the serialized frames as JSON response
        return JsonResponse({'frames': serialized_frames})
