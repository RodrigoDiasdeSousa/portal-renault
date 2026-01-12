import django_filters
from django import forms
from .models import SurveyResponse


class SurveyResponseFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date__gte",
        label="Data (de)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_before = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date__lte",
        label="Data (até)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    min_rating = django_filters.NumberFilter(field_name="overall_rating", lookup_expr="gte", label="Nota mín.")
    max_rating = django_filters.NumberFilter(field_name="overall_rating", lookup_expr="lte", label="Nota máx.")

    q = django_filters.CharFilter(method="filter_q", label="Busca (nome/email/vin/feedback)")

    class Meta:
        model = SurveyResponse
        fields = ["brand", "model", "location_name", "result_status", "origin", "activity"]

    def filter_q(self, queryset, name, value):
        v = (value or "").strip()
        if not v:
            return queryset
        return queryset.filter(
            customer_name__icontains=v
        ) | queryset.filter(
            email__icontains=v
        ) | queryset.filter(
            vin__icontains=v
        ) | queryset.filter(
            experience_feedback__icontains=v
        )
