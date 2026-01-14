import csv
import openpyxl
import json
from io import BytesIO
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django_filters.views import FilterView
from .models import SurveyResponse
from .filters import SurveyResponseFilter

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

class SurveyListView(LoginRequiredMixin, FilterView, ListView):
    model = SurveyResponse
    template_name = "pesquisas/survey_list.html"
    context_object_name = "surveys"
    filterset_class = SurveyResponseFilter
    paginate_by = 50
    ordering = ["-date"]

class SurveyDetailView(LoginRequiredMixin, DetailView):
    model = SurveyResponse
    template_name = "pesquisas/survey_detail.html"
    context_object_name = "survey"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        
        # --- LÓGICA DE FATIAR O NOME ---
        dealer_code = "-"
        nome_limpo = obj.location_name # Começa com o nome original

        if obj.location_name and "-" in obj.location_name:
            partes = obj.location_name.split("-")
            
            # Pega a primeira parte (Nome da Loja)
            nome_limpo = partes[0].strip()
            
            # Pega a última parte (Código)
            dealer_code = partes[-1].strip()
            
        context['codigo_extraido'] = dealer_code
        context['nome_loja_limpo'] = nome_limpo  # Nova variável para o HTML
        return context

# --- EXPORTAR CSV ---
def _load_schema(schema_name="base_csv_v1"):
    schema_path = Path(__file__).resolve().parent / "schemas" / f"{schema_name}.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _get_filtered_queryset(request):
    qs = SurveyResponse.objects.all().order_by("-date")
    survey_filter = SurveyResponseFilter(request.GET, queryset=qs)
    return survey_filter.qs


@login_required
def export_surveys_csv(request):
    schema = _load_schema("base_csv_v1")
    qs = _get_filtered_queryset(request)

    filename = f"pesquisas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # BOM para Excel (acentos OK)
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(schema)  # 152 colunas na ordem original

    for obj in qs.iterator(chunk_size=2000):
        raw = obj.raw_data or {}
        writer.writerow([raw.get(col, "") for col in schema])

    return response


@login_required
def export_surveys_xlsx(request):
    schema = _load_schema("base_csv_v1")
    qs = _get_filtered_queryset(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "Pesquisas"

    ws.append(schema)  # 152 colunas na ordem original

    for obj in qs.iterator(chunk_size=2000):
        raw = obj.raw_data or {}
        ws.append([raw.get(col, "") for col in schema])

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    filename = f"pesquisas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        bio.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
