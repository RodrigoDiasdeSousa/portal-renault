from django.urls import path
from .views import SurveyListView, export_surveys_csv, export_surveys_xlsx

app_name = "pesquisas"

urlpatterns = [
    path("", SurveyListView.as_view(), name="list"),
    path("export/csv/", export_surveys_csv, name="export_csv"),
    path("export/xlsx/", export_surveys_xlsx, name="export_xlsx"),
]
