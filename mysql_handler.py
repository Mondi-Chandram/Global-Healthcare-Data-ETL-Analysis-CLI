import mysql.connector
import logging

class MySQLHandler:
    def __init__(self, host, user, password, database):
        try:
            self.conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
            if self.conn.is_connected():
                logging.info("Successfully connected to MySQL database.")
        except mysql.connector.Error as err:
            logging.error(f"Failed to connect to MySQL database: {err}")
            raise
    def create_tables(self):
        cursor = self.conn.cursor()
        with open("sql/create_tables.sql", "r") as f:
            sql_script = f.read()
        for statement in sql_script.split(";"):
            if statement.strip():
                cursor.execute(statement)
        self.conn.commit()
        cursor.close()

    def insert_data(self, table_name, data_list):
        if not data_list:
            logging.info("DataFrame is empty. Nothing to insert.")
            return

        cursor = self.conn.cursor()

        select_sql = f"SELECT report_date, country_name FROM {table_name} WHERE report_date = %s AND country_name = %s"
        insert_sql = f"INSERT INTO {table_name} ({', '.join(data_list[0].keys())}) VALUES ({', '.join(['%s'] * len(data_list[0]))})"
        new_records = []

        for record in data_list:
            if 'date' in record:
                record['report_date'] = record.pop('date')
            if 'country' in record:
                record['country_name'] = record.pop('country')

            cursor.execute(select_sql, (record['report_date'], record['country_name']))
            if not cursor.fetchone():
                new_records.append(tuple(record.values()))

        if new_records:
            try:
                cursor.executemany(insert_sql, new_records)
                self.conn.commit()
                logging.info(f"Inserted {len(new_records)} new records into {table_name}.")
            except mysql.connector.Error as err:
                logging.error(f"Insert failed: {err}")
                self.conn.rollback()
        else:
            logging.info("No new records to insert.")

        cursor.close()


    def query_data(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        cursor.close()


    def query_scalar(self, sql, params=None):
        cursor = self.conn.cursor(buffered=True) 
        try:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()

    def query_data_with_result(self, query, params):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def list_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        if not tables:
            print()
            print("No tables found. Creating tables...")
            self.create_tables()
            print("Tables 'daily_cases', 'vaccination_data' created successfully.")
            print()
        else:
            print()
            print("Existing tables:")
            for table in tables:
                print(f"- {table}")
            print()
        cursor.close()


    def drop_tables(self):
        cursor = self.conn.cursor()

        try:
            cursor.execute("DROP TABLE IF EXISTS daily_cases")
            print()
            print("Dropped table: daily_cases")

            cursor.execute("DROP TABLE IF EXISTS vaccination_data")
            print("Dropped table: vaccination_data")
            print()

            self.conn.commit()
        except Exception as e:
            logging.error(f"Error while dropping tables: {e}")
            self.conn.rollback()
        finally:
            cursor.close()


    def close(self):
        self.conn.close()