import os

import psycopg2 as ps
from config import conf


def read_from_db(query: str, db_conf: dict) -> list:
    try:
        with ps.connect(**db_conf) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                response = cursor.fetchall()
                columns = [item.name for item in cursor.description]
                new_data = []
                for item in response:
                    new_data.append(dict(zip(columns, item)))
                return new_data
    except Exception as e:
        print(f"Failed to get data {e}")
        return [f"error: {e}"]


def execute_query(query: str, db_conf: dict):
    try:
        with ps.connect(**db_conf) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                print("Successful execution")
                return cursor.statusmessage

    except Exception as e:
        print(f"Failed to execute query {e}")
        return "Unsuccessful query execution"


if __name__ == '__main__':
    db_config = conf['database_config']
    db_config['password'] = os.environ['dbeaver_pass']
    print(read_from_db("select * from company.employees", db_config))
    execute_query("update company.employees set birth_date = '1978-09-01' where emp_name = 'Vlad'",
                  db_config)
    print(read_from_db("select * from company.employees", db_config))
