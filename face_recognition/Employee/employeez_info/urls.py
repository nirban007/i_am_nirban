from django.urls import path
from .views import EmployeeInfoListCreateAPIView, EmployeeInfoRetrieveUpdateDestroyAPIView, EmployeeImageListCreateAPIView, EmployeeImageRetrieveUpdateDestroyAPIView, LatestFramesView 
from .views import ImageView
from django.conf import settings
from django.conf.urls.static import static
# from .camera_views import stream_camera_feed
urlpatterns = [
    path('employee_info/', EmployeeInfoListCreateAPIView.as_view(), name='employee-info-list-create'),
    path('employee_info/<int:pk>/', EmployeeInfoRetrieveUpdateDestroyAPIView.as_view(), name='employee-info-retrieve-update-destroy'),
    path('employee_images/', EmployeeImageListCreateAPIView.as_view(), name='employee-image-list-create'),
    path('employee_images/<int:pk>/', EmployeeImageRetrieveUpdateDestroyAPIView.as_view(), name='employee-image-retrieve-update-destroy'),
    path('images/', ImageView.as_view(), name='image-view'),
    path('employee/images/', LatestFramesView.as_view(), name='stream_camera_feed'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

