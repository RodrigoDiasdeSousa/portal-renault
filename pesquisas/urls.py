from django.urls import path
from .views import HomeView, SurveyListView, SurveyDetailView, export_surveys_csv, export_surveys_xlsx

app_name = "pesquisas"

urlpatterns = [
    # Home (Dashboard com os cartões)
    path("", HomeView.as_view(), name="home"), 

    # Lista (Tabela de dados) - Mudei para 'lista/' para não bater com a home
    path("lista/", SurveyListView.as_view(), name="list"),

    # Detalhes e Exportações
    path('<int:pk>/', SurveyDetailView.as_view(), name='detail'),
    path("export/csv/", export_surveys_csv, name="export_csv"),
    path("export/xlsx/", export_surveys_xlsx, name="export_xlsx"),
]