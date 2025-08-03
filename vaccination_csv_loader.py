import pandas as pd
from mysql_handler import MySQLHandler

class VaccinationCSVLoader:
    def __init__(self, db: MySQLHandler):
        self.db = db

    def load_csv(self, file_path: str):
        df = pd.read_csv(file_path)

        df = df.rename(columns={
            "COUNTRY": "country_name",
            "COVID_VACCINE_ADM_TOT_DOSES": "total_vaccinations",
            "COVID_VACCINE_ADM_TOT_A1D": "people_vaccinated",
            "COVID_VACCINE_ADM_TOT_CPS": "people_fully_vaccinated",
            "DATE": "report_date"
        })

        df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
        df = df.dropna(subset=["report_date", "country_name"])
        df = df.sort_values("report_date").drop_duplicates(subset=["country_name"], keep="last")

        data_to_insert = df[[
            "report_date", "country_name", "total_vaccinations",
            "people_vaccinated", "people_fully_vaccinated"
        ]].to_dict(orient="records")

        self.db.insert_data('vaccination_data', data_to_insert)
        print()
        print(f"Loaded {len(data_to_insert)} vaccination records.")
        print()
