"""Utility module for common and extra things."""

import hashlib
import os
from urllib.parse import urlparse

import pandas as pd
import psycopg2


class General:
    """General functions class."""

    def get_conn():
        """Get connection to PostgreSQL database."""
        conn = None
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="stream_scrape",
                user="postgres",
                password="password",
            )
            print("Connected to PostgreSQL database!")
        except Exception as e:
            print(f"Error connecting to PostgreSQL database: {e}")
        return conn

    def data_preprocessing(df):
        """Preprocessing & cleanup."""
        try:
            # Function to unescape HTML entities in a string values of df
            # df = df.applymap(lambda x: html.unescape(x) if isinstance(x, str) else x)
            df.replace("&amp;", "&", regex=True, inplace=True)
            df.replace("\u200e", "", regex=True, inplace=True)
            df.replace("\\xa0", " ", regex=True, inplace=True)
            df = df.replace("nan", "None")
            df = df.replace("'", "''", regex=True)
            df = df.replace('"', "", regex=True)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.replace("\u000b", "", regex=True)
            df = df.replace("\r", "", regex=True)
            # df = df.replace("\n","",regex=True)
            df = df.replace("\xa0", "", regex=True)
            df = df.replace("\u200b", "", regex=True)
            df = df.replace("\u3000", "", regex=True)
        except Exception as e:
            line_number = e.__traceback__.tb_lineno
            print(f"error in Data preprocessing at line no : {line_number} \n {e}")
        return df

    def extract_domain(url):
        """Get domain from url."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain

    def generate_query(df, table_name, ret_key, update=False):
        """Generate SQL query using dataframe."""
        df = General.data_preprocessing(df)

        field_names = list(df)
        col_names = ",".join(["" + str(i) + "" for i in field_names])

        df.fillna("None", inplace=True)

        tuple_value = list(df.to_records(index=False))
        tuple_value = str(tuple_value)[1:-1]
        val_for_query = (
            tuple_value.replace("None", "NULL")
            .replace("'null'", "NULL")
            .replace("'NULL'", "NULL")
            .replace('"', "'")
        )

        if update is False:

            q_string = f""" INSERT INTO {table_name} ({col_names}) VALUES
                            {val_for_query} ON CONFLICT DO NOTHING
                            RETURNING id as {ret_key} ; """

            return q_string

        else:

            q_string = f""" INSERT INTO {table_name} ({col_names})
                            VALUES {val_for_query} {update}
                            RETURNING id as {ret_key} ; """

            return q_string

    def run_query(query, conn, write=False):
        """Run query on db."""
        if not write:  # read query
            cur = conn.cursor()
            cur.execute(query)
            res = cur.fetchall()
            return res
        else:
            cur = conn.cursor()
            cur.execute(query)
            res = cur.fetchall()
            if os.getenv("IS_COMMIT", "true").lower() in ("true"):
                conn.commit()
            else:
                print("commit is false")
            return res


class Marketplace:
    """Marketplace level class for each marketplace hashcode function."""

    def amazon(url):
        """Hashcode generation for Amazon URL."""
        url = url.split("?")[0]
        link = urlparse(str(url))
        ids = link.path.split("/")

        # adding domain to avoid country's conflict
        domain = General.extract_domain(url)

        final_str = domain + ids[2] + ids[3]
        secure_hash = hashlib.md5(final_str.encode()).hexdigest()
        return secure_hash
