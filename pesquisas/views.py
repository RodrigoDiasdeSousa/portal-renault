import csv
import openpyxl
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
def export_surveys_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pesquisas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data', 'Loja', 'Cód. Loja', 'Marca', 'Modelo', 'Nota', 'Feedback', 'Status'])

    qs = SurveyResponse.objects.all().order_by('-date')
    survey_filter = SurveyResponseFilter(request.GET, queryset=qs)
    
    for obj in survey_filter.qs:
        nome_limpo = obj.location_name
        dealer_code = "-"
        
        if obj.location_name and "-" in obj.location_name:
            partes = obj.location_name.split("-")
            nome_limpo = partes[0].strip()
            dealer_code = partes[-1].strip()
        
        writer.writerow([
            obj.date.strftime("%d/%m/%Y"),
            nome_limpo,   # Exporta só o nome limpo
            dealer_code,  # Exporta o código separado
            obj.brand,
            obj.model,
            obj.overall_rating,
            obj.experience_feedback,
            obj.result_status
        ])
    return response

# --- EXPORTAR EXCEL ---
def export_surveys_xlsx(request):
    qs = SurveyResponse.objects.all().order_by('-date')
    survey_filter = SurveyResponseFilter(request.GET, queryset=qs)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pesquisas"
    ws.append(['Data', 'Loja', 'Cód. Loja', 'Marca', 'Modelo', 'Nota', 'Feedback', 'Status'])

    for obj in survey_filter.qs:
        data_str = obj.date.strftime("%d/%m/%Y") if obj.date else ""
        
        nome_limpo = obj.location_name
        dealer_code = "-"
        
        if obj.location_name and "-" in obj.location_name:
            partes = obj.location_name.split("-")
            nome_limpo = partes[0].strip()
            dealer_code = partes[-1].strip()

        ws.append([
            data_str,
            nome_limpo,  # Exporta só o nome limpo
            dealer_code, # Exporta o código separado
            obj.brand,
            obj.model,
            obj.overall_rating,
            obj.experience_feedback,
            obj.result_status
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="pesquisas.xlsx"'
    wb.save(response)
    return response