from django.db import models
import os

class employee_info(models.Model):
    e_id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=50,unique=True)
    nid_no = models.CharField(max_length=100,unique=True)
    
def employee_image_directory_path(instance, filename):
    # The function returns the upload path for the image
    return f'employee_images/{instance.employee.e_id}/{filename}'

class EmployeeImage(models.Model):
    employee = models.ForeignKey(employee_info, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=employee_image_directory_path)
    
def get_upload_path(instance, filename):
    return os.path.join('captured', filename)


class ImageModel(models.Model):
    marked_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=get_upload_path)

    def __str__(self):
        return f"Image {self.id}"
