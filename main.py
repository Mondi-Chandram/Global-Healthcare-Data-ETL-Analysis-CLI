import argparse
import configparser
import logging
from api_client import APIClient
from data_transformer import DataTransformer
from mysql_handler import MySQLHandler
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def main():
    config = load_config()

    db = MySQLHandler(
        config['mysql']['host'],
        config['mysql']['user'],
        config['mysql']['password'],
        config['mysql']['database']
    )
    api = APIClient(config['api']['base_url'], config['api'].get('api_key'))
    transformer = DataTransformer()

    parser = argparse.ArgumentParser(description="Healthcare ETL CLI")
    subparsers = parser.add_subparsers(dest='command')

    fetch_parser = subparsers.add_parser('fetch_data')
    fetch_parser.add_argument('--country', required=True)
    fetch_parser.add_argument('--start_date')
    fetch_parser.add_argument('--end_date')
    fetch_parser.add_argument('--date')

    query_parser = subparsers.add_parser('query_data')
    query_parser.add_argument('column')
    query_parser.add_argument('country')
    query_parser.add_argument('extra_column', nargs='?', default=None)

    subparsers.add_parser('list_tables')
    subparsers.add_parser('drop_tables')

    subparsers.add_parser("load_vaccination_data")

    args = parser.parse_args()

    if args.command == 'fetch_data':
        
        params = {'country': args.country}
        if args.date:
            params['date'] = args.date
        print()
        print(f"Fetching data for {args.country} from {args.start_date or 'beginning'} to {args.end_date or 'latest'}...")

        raw_data = api.fetch_data(params=params)
        if not raw_data:
            logging.warning("No data returned from API. Skipping transformation and insertion.")
            return

        cleaned = transformer.clean_and_transform(raw_data, start_date=args.start_date, end_date=args.end_date)

        if cleaned.empty:
            logging.warning("No cleaned records to insert. Skipping DB insertion.")
            return
        
        print("Cleaned and transformed data.")

        db.create_tables()

        if not cleaned.empty:
            data_to_insert = cleaned.to_dict(orient="records")  
            db.insert_data('daily_cases', data_to_insert)
            print(f"Loaded {len(data_to_insert)} records into 'daily_cases' table.")
            print()
        else:
            logging.info("No data to insert: cleaned DataFrame is empty.")

    elif args.command == 'query_data':
        if args.column == 'daily_trends' and args.extra_column:
            sql = f"""
                SELECT report_date, {args.extra_column}
                FROM daily_cases
                WHERE country_name = %s
                ORDER BY report_date ASC
            """
            rows = db.query_data_with_result(sql, (args.country,))
            if not rows:
                print("No data found.")
            else:
                print(f"Date       | {args.extra_column.replace('_', ' ').title()}")
                print("-" * 30)
                for date, value in rows:
                    print(f"{date} | {value}")
                print()
            return
        
        elif args.column == 'top_n_countries_by_metric':
            try:
                top_n = int(args.country)  
                metric = args.extra_column  
                sql = f"""
                    SELECT country_name, MAX({metric}) AS total
                    FROM vaccination_data
                    GROUP BY country_name
                    ORDER BY total DESC
                    LIMIT %s
                """
                rows = db.query_data_with_result(sql, (top_n,))
                if not rows:
                    print("No data found.")
                else:
                    print()
                    print("Rank | Country         | " + metric.replace("_", " ").title())
                    print("-------------------------------------------")
                    for idx, (country, total) in enumerate(rows, 1):
                        print(f"{idx:<4} | {country:<15} | {total:,}")
                    print()
            except Exception as e:
                print(f"[ERROR] Could not execute top_n query: {e}")
            return

        else:
            sql = f"""
                select max({args.column})
                from daily_cases
                where country_name = %s
                """
            
        result = db.query_scalar(sql, (args.country,))
        if result is not None:
            print()
            print(f"Total COVID-19 {args.column.replace('_', ' ').title()} in {args.country}: {result}")
            print()
        else:
            print()
            print("No data found.")
            print()

    elif args.command == 'load_vaccination_data':
        from vaccination_csv_loader import VaccinationCSVLoader
        db.create_tables()
        loader = VaccinationCSVLoader(db)
        loader.load_csv("vaccinations.csv")

    elif args.command == 'list_tables':
        db.list_tables()

    elif args.command == 'drop_tables':
        db.drop_tables()

    db.close()

if __name__ == "__main__":
    main()