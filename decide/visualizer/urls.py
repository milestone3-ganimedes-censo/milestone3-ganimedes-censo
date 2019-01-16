from django.urls import path
from .views import VisualizerView, VisualizerPdf, VisualizerCsv, VisualizerJson, VisualizerXml, VisualizerList

urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('<int:voting_id>/pdf/', VisualizerPdf.as_view()),
    path('<int:voting_id>/csv/', VisualizerCsv.as_view()),
    path('<int:voting_id>/json/', VisualizerJson.as_view()),
    path('<int:voting_id>/xml/', VisualizerXml.as_view()),
    path('list_ended/', VisualizerList.as_view()),
]
