# Global Healthcare ETL & CLI Project

## Overview
Build a robust command-line application that extracts healthcare data from a public API, transforms it into a clean and
structured format, loads it into a MySQL database, and allows users to perform basic analytical queries directly from the
CLI. This project emphasizes critical data engineering skills like data ingestion, cleaning, and storage for analytical
purposes.

## Setup
- Configure `config.ini` with your database and API details
- Create MySQL database and run `create_tables.sql`
- Install dependencies: `pip install -r requirements.txt`

## Details of the chosen public API and its data.
- [api]
- base_url = https://api.api-ninjas.com/v1/covid19
- api_key = my_api_key_here

## CLI command usage guide with examples.

- List database tables:
```bash
python main.py list_tables
```
- Fetch data:
```bash
python main.py fetch_data --country "India"
```
```bash
python main.py fetch_data --country "India" --start_date 2023-01-01 --end_date 2023-01-31
```
```bash
python main.py fetch_data --country "United States" --start_date 2023-01-01 --end_date 2023-01-31
```
- Query total cases:
```bash
python main.py query_data total_cases "India"
```
- Query new_cases
```bash
python main.py query_data daily_trends "India" new_cases
```
- Load Vacination_data
```bash
python main.py load_vaccination_data
```
- Getting top 3 countries by total vaccinations
```bash
python main.py query_data top_n_countries_by_metric 3 total_vaccinations
```
- Drop all tables:
```bash
python main.py drop_tables
```

## Database Schema Description

The project uses two primary MySQL tables to store COVID-19 case and vaccination data. Below is the detailed schema for each:

---

### Table: `daily_cases`

| Column Name    | Data Type   | Constraints                                               | Description                          |
|----------------|-------------|------------------------------------------------------------|--------------------------------------|
| `id`           | INT         | PRIMARY KEY, AUTO_INCREMENT                               | Unique record ID                     |
| `report_date`  | DATE        | NOT NULL, part of UNIQUE (`country_name`, `report_date`) | Date of the report                   |
| `country_name` | VARCHAR(255)| NOT NULL                                                 | Name of the country                  |
| `total_cases`  | BIGINT      | NULLABLE                                                 | Cumulative reported cases            |
| `new_cases`    | INT         | NULLABLE                                                 | New cases on that date               |
| `total_deaths` | BIGINT      | NULLABLE                                                 | Cumulative reported deaths           |
| `new_deaths`   | INT         | NULLABLE                                                 | New deaths on that date              |
| `etl_timestamp`| TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP                                | Timestamp when the record was loaded |

---

### Table: `vaccination_data`

| Column Name                | Data Type   | Constraints                                               | Description                              |
|----------------------------|-------------|------------------------------------------------------------|------------------------------------------|
| `id`                       | INT         | PRIMARY KEY, AUTO_INCREMENT                               | Unique record ID                         |
| `report_date`              | DATE        | NOT NULL, part of UNIQUE (`country_name`, `report_date`) | Date of the report                       |
| `country_name`             | VARCHAR(255)| NOT NULL                                                 | Name of the country                      |
| `total_vaccinations`       | BIGINT      | NULLABLE                                                 | Total doses administered                 |
| `people_vaccinated`        | BIGINT      | NULLABLE                                                 | People who received at least one dose    |
| `people_fully_vaccinated`  | BIGINT      | NULLABLE                                                 | People who are fully vaccinated          |
| `etl_timestamp`            | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP                                | Timestamp when the record was loaded     |

## ETL Process Description

This project follows a traditional **Extract, Transform, Load (ETL)** workflow to collect, process, and store global COVID-19 healthcare data into a MySQL database.

---

### 1. Extract

- **Source APIs:**
  - **COVID-19 Cases API:** [API Ninjas COVID-19](https://api.api-ninjas.com/v1/covid19)
  - **Vaccination Data:** WHO dataset (CSV file `vaccinations.csv`)
- **Fetch Mechanism:**
  - The application uses an `APIClient` class to send GET requests to the API.
  - Supports fetching full history or filtered data using optional parameters: `--start_date`, `--end_date`, or a specific `--date`.

---

### 2. Transform

- Handled by the `DataTransformer` class.
- Cleans and normalizes raw JSON or CSV data:
  - Filters data by date ranges (if specified).
  - Renames fields to match database schema.
  - Converts data types (e.g., strings to dates or integers).
  - Handles missing or null values safely.

---

### 3. Load

- Managed by the `MySQLHandler` class.
- Creates MySQL tables (`daily_cases`, `vaccination_data`) if they don't exist.
- Inserts cleaned records into the appropriate tables.
- Uses `etl_timestamp` to track when records were inserted.
- Prevents duplicate entries using a composite uniqueness constraint on `country_name` + `report_date`.

---

### 🔁 CLI Command Flow

- `python main.py fetch_data --country "India"`  
  → Extracts from API → Transforms → Loads into `daily_cases`.

- `python main.py load_vaccination_data`  
  → Reads WHO CSV → Transforms → Loads into `vaccination_data`.

---

This ETL pipeline ensures data is up-to-date, reliable, and queryable for analytics using CLI commands.


## Known Limitations and Future Improvements

### Known Limitations

- **Limited API Query Parameters:**
  - The current COVID-19 API only supports queries by country and an optional date. It does not natively support date ranges (`start_date`, `end_date`), so date filtering is handled post-fetch in Python.

- **No API Pagination Handling:**
  - The API returns all available data in one response. While sufficient for small datasets, this could lead to performance issues for larger datasets if the API size increases.

- **Single-Country Fetch per Command:**
  - Data can be fetched for one country at a time only. Batch fetching or parallel extraction is not implemented.

---

### Future Improvements

- **API Enhancements:**
  - Upgrade to an API that supports full date range queries and pagination.
  - Add retries and backoff logic for robust network handling.

- **Data Upserts:**
  - Implement upsert functionality to update records if a newer version of the same report is fetched.

- **Parallel Processing:**
  - Allow fetching data for multiple countries concurrently to reduce runtime.

- **Web Dashboard (Optional):**
  - Build a simple web-based dashboard to visualize trends instead of using CLI only.


