from django.urls import path, re_path

from .data_views import PlantDataPointsView
from .report_views import ReportView
from .views import PlantApiView, PlantDetailsView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', PlantApiView.as_view(), name='plant'),
    path('plant/<str:plant_id>', PlantDetailsView.as_view(), name='plant_details'),
    re_path(r'data/$', PlantDataPointsView.as_view(), name='data'),
    re_path(r'report/$', ReportView.as_view(), name='report')
]
