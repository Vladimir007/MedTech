from django.urls import path, re_path
from contacts import views


urlpatterns = [
    path('create/', views.CreateContactView.as_view(), name='create'),
    path('details/<int:pk>/', views.InspectContactView.as_view(), name='inspect'),
    path('edit/<int:pk>/', views.EditContactView.as_view(), name='edit'),
    path('delete/<int:pk>/', views.DeleteContactView.as_view(), name='delete'),
    path('company/<int:pk>/', views.InspectCompanyView.as_view(), name='company'),
    path('import/', views.ImportContactsView.as_view(), name='import'),
    path('export/', views.ExportContactsView.as_view(), name='export'),
    path('parse-web/', views.ParseWebsite.as_view(), name='parse'),
]