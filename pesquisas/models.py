from django.db import models

class SurveyResponse(models.Model):
    # IDs (para deduplicar)
    external_id = models.CharField(max_length=64, blank=True, db_index=True)  # "External Id" (uuid)
    survey_id = models.CharField(max_length=64, blank=True, db_index=True)   # "id" (id do survey)

    # Loja / Local
    location_code = models.CharField(max_length=32, blank=True, db_index=True)   # Location Code
    location_name = models.CharField(max_length=200, blank=True, db_index=True) # Location Name
    dealer_id = models.CharField(max_length=32, blank=True, db_index=True)      # Dealer Id

    # Classificações úteis
    activity = models.CharField(max_length=32, blank=True, db_index=True)       # activity (ex: Sales)
    origin = models.CharField(max_length=32, blank=True, db_index=True)         # Origin (Mobile/Desktop)
    result_status = models.CharField(max_length=32, blank=True, db_index=True)  # Result Status
    country_code = models.CharField(max_length=8, blank=True, db_index=True)    # country_code (BR)

    # Datas
    date = models.DateTimeField(db_index=True)        # Date
    final_date = models.DateTimeField(null=True, blank=True)  # Final Date

    # Cliente (se quiser manter; dá pra mascarar na UI depois)
    customer_name = models.CharField(max_length=300, blank=True)
    email = models.EmailField(blank=True)
    mobile_phone = models.CharField(max_length=40, blank=True)

    # Veículo
    vin = models.CharField(max_length=40, blank=True, db_index=True)
    brand = models.CharField(max_length=20, blank=True, db_index=True)   # BRAND (ex: REN)
    model = models.CharField(max_length=80, blank=True, db_index=True)   # MODEL (ex: Oroch)

    # Nota / feedback
    overall_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, db_index=True)
    experience_feedback = models.TextField(blank=True)
    additional_feedback = models.TextField(blank=True)
    anonymity = models.CharField(max_length=120, blank=True)
    # Linha original completa do CSV (todas as colunas)
    raw_data = models.JSONField(null=True, blank=True)
    raw_schema_name = models.CharField(max_length=50, default="base_csv_v1")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["external_id", "survey_id"], name="uniq_external_survey"),
        ]
        ordering = ["-date", "-id"]

    @property
    def loja_formatada(self):
        if self.location_name and "-" in self.location_name:
            # Pega só a primeira parte (o nome)
            return self.location_name.split("-")[0].strip()
        return self.location_name

    # ISSO É VIRTUAL. NÃO VAI PRO BANCO DE DADOS.
    @property
    def bir_code(self):
        if self.location_name and "-" in self.location_name:
            # Pega só a última parte (o código)
            return self.location_name.split("-")[-1].strip()
        return "-"

    def __str__(self):
        return f"{self.date} | {self.location_name} | {self.model} | {self.overall_rating}"
