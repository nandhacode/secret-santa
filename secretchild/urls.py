from django.urls import path
from . import views

urlpatterns = [
    path('', views.secret_santa, name='secret_santa'),
    path('upload-employees/', views.upload_employee_csv, name='upload_employee_csv'),
    path('upload-previous-secretsanta/', views.upload_previous_secretchild_data, name='upload_previous_secretsanta_csv'),
    path('generate-secret-children/', views.assign_secret_santa_children, name='generate_secret_santa'),
    path('generate-secret-children-download/', views.download_secret_santa_csv, name='generate_secret_santa_download'),
]