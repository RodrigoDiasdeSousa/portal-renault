from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django_filters.views import FilterView

from .models import SurveyResponse
from .filters import SurveyResponseFilter

class SurveyListView(LoginRequiredMixin, FilterView, ListView):
    model = SurveyResponse
    template_name = "pesquisas/survey_list.html"
    context_object_name = "surveys"
    filterset_class = SurveyResponseFilter
    paginate_by = 50
    ordering = ["-date"]
