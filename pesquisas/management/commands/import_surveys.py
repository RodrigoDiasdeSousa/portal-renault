import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.timezone import make_aware

from pesquisas.models import SurveyResponse


def parse_decimal_pt(v: str):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    # "5,00" -> "5.00"
    s = s.replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def parse_dt(v: str):
    s = (v or "").strip()
    if not s:
        return None
    # seu arquivo: "12/31/2024 23:18:55" (MM/DD/YYYY)
    dt = datetime.strptime(s, "%m/%d/%Y %H:%M:%S")
    return make_aware(dt)


class Command(BaseCommand):
    help = "Importa pesquisas do CSV exportado do portal antigo (delimitador ';')."

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str, help="Caminho do arquivo base.csv")
        parser.add_argument("--delimiter", type=str, default=";", help="Delimitador do CSV (padrão ';')")

    @transaction.atomic
    def handle(self, *args, **opts):
        filepath = opts["filepath"]
        delimiter = opts["delimiter"]

        try:
            f = open(filepath, "r", encoding="utf-8-sig", newline="")
        except FileNotFoundError:
            raise CommandError(f"Arquivo não encontrado: {filepath}")

        created = updated = skipped = 0

        with f:
            reader = csv.DictReader(f, delimiter=delimiter)
            if not reader.fieldnames:
                raise CommandError("Não consegui ler o cabeçalho. Confirme delimitador/arquivo.")

            required = ["Date", "External Id", "id"]
            missing = [c for c in required if c not in reader.fieldnames]
            if missing:
                raise CommandError(f"Colunas obrigatórias não encontradas: {missing}")

            for row in reader:
                date = parse_dt(row.get("Date"))
                if not date:
                    skipped += 1
                    continue

                final_date = parse_dt(row.get("Final Date"))

                external_id = (row.get("External Id") or "").strip()
                survey_id = (row.get("id") or "").strip()

                customer_name = " ".join([
                    (row.get("CUSTOMER_NAME_1") or "").strip(),
                    (row.get("CUSTOMER_NAME_2") or "").strip(),
                    (row.get("CUSTOMER_SURNAME_1") or "").strip(),
                    (row.get("CUSTOMER_SURNAME_2") or "").strip(),
                ]).strip()
                
                raw = dict(row)
                
                defaults = dict(
                    # loja/local
                    location_code=(row.get("Location Code") or "").strip(),
                    
                    # --- AQUI ESTAVA O ERRO ---
                    # Antes: row.get("Location Name") -> Pegava só "Orvel Vila Velha"
                    # Agora: row.get("Location Internal Name") -> Pega "Orvel Vila Velha - RENAULT - 07601179"
                    location_name=(row.get("Location Internal Name") or "").strip(),
                    # --------------------------

                    dealer_id=(row.get("Dealer Id") or "").strip(),

                    # classificação
                    activity=(row.get("activity") or "").strip(),
                    origin=(row.get("Origin") or "").strip(),
                    result_status=(row.get("Result Status") or "").strip(),
                    country_code=(row.get("country_code") or "").strip(),

                    # datas
                    date=date,
                    final_date=final_date,

                    # cliente
                    customer_name=customer_name,
                    email=(row.get("E_MAIL_1") or "").strip(),
                    mobile_phone=(row.get("MOBILE_PHONE_1") or "").strip(),

                    # veículo
                    vin=(row.get("vin") or "").strip(),
                    brand=(row.get("BRAND") or "").strip(),
                    model=(row.get("MODEL") or "").strip(),

                    # nota/feedback
                    overall_rating=parse_decimal_pt(row.get("overall_rating")),
                    experience_feedback=(row.get("experience_feedback") or "").strip(),
                    additional_feedback=(row.get("additional_feedback") or "").strip(),
                    anonymity=(row.get("anonymity") or "").strip(),
                    raw_data=raw,
                    raw_schema_name="base_csv_v1",
                )

                obj, was_created = SurveyResponse.objects.update_or_create(
                    external_id=external_id,
                    survey_id=survey_id,
                    defaults=defaults,
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import finalizado: created={created}, updated={updated}, skipped={skipped}"
        ))