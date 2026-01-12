import csv
import json
from io import BytesIO
from datetime import datetime
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView
from django_filters.views import FilterView

from openpyxl import Workbook

from .filters import SurveyResponseFilter
from .models import SurveyResponse


# ---------- HOME ----------
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"


# ---------- LISTAGEM + FILTROS ----------
class SurveyListView(LoginRequiredMixin, FilterView, ListView):
    model = SurveyResponse
    template_name = "pesquisas/survey_list.html"
    context_object_name = "surveys"
    filterset_class = SurveyResponseFilter
    paginate_by = 50
    ordering = ["-date"]


def _get_filtered_queryset(request):
    base_qs = SurveyResponse.objects.all().order_by("-date")
    f = SurveyResponseFilter(request.GET, queryset=base_qs)
    return f.qs


def _load_schema(schema_name="base_csv_v1"):
    """
    Carrega a lista de colunas na ordem exata do CSV original.
    Espera o arquivo: pesquisas/schemas/<schema_name>.json
    """
    schema_path = Path(__file__).resolve().parent / "schemas" / f"{schema_name}.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


# ---------- EXPORTAÇÃO (FORMATO ORIGINAL) ----------
@login_required
def export_surveys_csv(request):
    qs = _get_filtered_queryset(request)

    schema_name = "base_csv_v1"
    schema = _load_schema(schema_name)

    filename = f"pesquisas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # BOM para Excel (acentos OK)
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow(schema)  # header ORIGINAL

    for obj in qs.iterator(chunk_size=2000):
        raw = obj.raw_data or {}
        writer.writerow([raw.get(col, "") for col in schema])

    return response


@login_required
def export_surveys_xlsx(request):
    qs = _get_filtered_queryset(request)

    schema_name = "base_csv_v1"
    schema = _load_schema(schema_name)

    wb = Workbook()
    ws = wb.active
    ws.title = "Pesquisas"

    ws.append(schema)  # header ORIGINAL

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
