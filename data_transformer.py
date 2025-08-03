import pandas as pd

class DataTransformer:
    def clean_and_transform(self, raw_data, start_date=None, end_date=None):
        if not raw_data or 'country' not in raw_data[0] or 'cases' not in raw_data[0]:
            raise ValueError("Invalid data format received from API")

        country = raw_data[0]['country']
        cases = raw_data[0]['cases']

        rows = []
        for date_str, data in cases.items():
            row = {
                'country': country,
                'date': date_str,
                'total_cases': data.get('total', 0),
                'new_cases': data.get('new', 0)
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        df['date'] = pd.to_datetime(df['date'])
        df['total_cases'] = pd.to_numeric(df['total_cases'], errors='coerce')
        df['new_cases'] = pd.to_numeric(df['new_cases'], errors='coerce')

        df.drop_duplicates(subset=['country', 'date'], inplace=True)

        df.rename(columns={'country': 'country_name', 'date': 'report_date'}, inplace=True)

        if start_date:
            df = df[df['report_date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['report_date'] <= pd.to_datetime(end_date)]

        return df
