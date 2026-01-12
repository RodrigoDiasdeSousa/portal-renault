from django.contrib import admin
from .models import SurveyResponse

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("date", "location_name", "brand", "model", "overall_rating", "result_status", "origin", "activity")
    list_filter = ("brand", "model", "result_status", "origin", "activity", "location_name")
    search_fields = ("customer_name", "email", "vin", "experience_feedback", "external_id", "survey_id")
    date_hierarchy = "date"
    ordering = ("-date", "-id")


# Register your models here.
