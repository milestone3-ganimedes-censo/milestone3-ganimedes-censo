from django.urls import path, include
from census.views import add_custom_census, export_csv, import_csv
from . import views


urlpatterns = [

    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('addAllRegistered/', views.addAllRegistered, name='addAllRegistered'),
    path('addAllInCity/', views.addAllInCity, name='addAllInCity'),
    path('addAllBySex/', views.addAllBySex, name='addAllBySex'),
    path('addAllByAge/', views.addAllByAge, name='addAllByAge'),
    path('addCustomCensus', add_custom_census, name='addCustomCensus'),
    path('exportCensus', export_csv, name='exportCSV'),
    path('importCensus', import_csv, name='importCSV'),
    path('viewVoters', views.viewVoters, name='viewVoters'),
    path('createCensus', views.passVotings, name='passVotings'),
    path('exportCensusView', views.export_csv_view, name='exportCSVView'),
    path('importCensusView', views.import_csv_view, name='importCSVView'),
    path('listCensus', views.list_census, name='listCensus'),
    path('editCensus', views.edit_census, name='editCensus'),
    path('deleteCensus', views.delete_census, name='deleteCensus'),
    path('saveEditedCensus', views.save_edited_census, name='saveEditedCensus'),
    path('deleteSelectedCensus', views.delete_selected_census, name='deleteSelectedCensus'),

]