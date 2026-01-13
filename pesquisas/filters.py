import django_filters
from django import forms
from .models import SurveyResponse

class SurveyResponseFilter(django_filters.FilterSet):
    # Campos de Data
    date_after = django_filters.DateFilter(
        field_name="date", lookup_expr="gte", label="Data (de)",
        widget=forms.DateInput(attrs={"type": "date"})
    )
    date_before = django_filters.DateFilter(
        field_name="date", lookup_expr="lte", label="Data (até)",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    # Busca Geral
    q = django_filters.CharFilter(method="filter_q", label="Busca Geral")

    # Ordenação
    ordering = django_filters.OrderingFilter(
        fields=(('date', 'date'), ('overall_rating', 'rating')),
        field_labels={
            'date': 'Data (Mais Antigos)',
            '-date': 'Data (Mais Recentes)',
            'rating': 'Nota (Menor -> Maior)',
            '-rating': 'Nota (Maior -> Menor)',
        },
        label="Ordenar por",
        empty_label="Padrão (Mais Recentes)"
    )

    # --- NOVO: Filtro Exato de Estrelas ---
    rating_exact = django_filters.MultipleChoiceFilter(
        field_name='overall_rating',
        lookup_expr='exact',
        label="Filtrar Notas",
        widget=forms.CheckboxSelectMultiple, # Isso permite selecionar vários
        choices=[
            (5, "5"),
            (4, "4"),
            (3, "3"),
            (2, "2"),
            (1, "1"),
        ]
    )

    class Meta:
        model = SurveyResponse
        fields = ["brand", "model", "location_name", "result_status", "origin", "activity"]

    def filter_q(self, queryset, name, value):
        v = (value or "").strip()
        if not v: return queryset
        return queryset.filter(
            customer_name__icontains=v
        ) | queryset.filter(
            email__icontains=v
        ) | queryset.filter(
            vin__icontains=v
        ) | queryset.filter(
            experience_feedback__icontains=v
        )