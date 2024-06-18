"""Streamlit app UI."""

import os
from datetime import datetime

import pandas as pd
import streamlit as st
from utils import General, Marketplace


class StreamScrape:
    """Main Class."""

    def add_product(self):
        """Add product to track."""
        # setting default option
        default_option = ["Please select any option"]

        action_options = ["Add Product", "Edit Product", "Delete Product"]
        selected_option = st.radio(
            "**Select Action:**",
            action_options,
            index=0,
            key="stream_scrape_radio_1",
            horizontal=True,
        )

        if selected_option == action_options[0]:
            with st.form("My Form"):

                # Input field for product name
                product_name = st.text_input(
                    "**Enter Product Name:**", key="stream_scrape_select_1"
                )

                # Input field for product urls
                product_url = st.text_input(
                    "**Enter Product URL:**", key="stream_scrape_select_2"
                )

                # Select box for choosing processing frequency
                frequency_options = [
                    "Every 1 hour",
                    "Every 3 Hours",
                    "Every 6 Hours",
                    "Every 12 Hours",
                    "Daily",
                ]
                selected_frequency = st.selectbox(
                    "**Select Processing Frequency:**",
                    default_option + frequency_options,
                    key="env_editor_select_3",
                )

                # Submit button
                submitted = st.form_submit_button(
                    "RUN",
                    type="primary",
                    help="Click the button to see the FM/ETL results.",
                )

            with st.container():
                # Display the submitted data
                if submitted:
                    if product_name == "" or product_url == "":
                        st.error("Please Enter Product Name and URL!")
                    else:
                        conn = None
                        try:
                            # st.write(f'Name: {product_name}, URL: {product_url},
                            #  Frequency: {selected_frequency}')
                            hashcode = Marketplace.amazon(url=product_url)
                            if hashcode is not None:

                                # create dataframe and generate insert query
                                df_product = pd.DataFrame()
                                df_product["name"] = [product_name]
                                df_product["url"] = product_url
                                df_product["created_at"] = datetime.now()
                                df_product["updated_at"] = datetime.now()
                                df_product["frequency"] = selected_frequency
                                df_product["hashcode"] = hashcode

                                query_insert = General.generate_query(
                                    df=df_product, table_name="products", ret_key="id"
                                )
                                # st.write(query_insert)

                                # get connection and run query
                                conn = General.get_conn()
                                res_df = pd.read_sql(query_insert, con=conn)

                                # commit only if commit env is true
                                # (helpful for development)
                                if (
                                    os.getenv("IS_COMMIT", "false").strip().lower()
                                    == "true"
                                ):
                                    conn.commit()
                                conn.close()

                                st.write(res_df)
                            else:
                                st.error(
                                    "Error in Hashcode Genration !"
                                    "Please contact admin."
                                )

                        except Exception as e:
                            if conn:
                                conn.rollback()
                            st.error(f"line no: {e.__traceback__.tb_lineno}")
                            st.error(e)

                        finally:
                            if conn:
                                conn.close()

    def run(self):
        """Start point runner function."""
        st.set_page_config(page_title="StreamScrape", layout="wide")
        st.title("StreamScrape")

        tabs = st.tabs(["Home", "Editor", "About"])

        with tabs[0]:
            st.write("developement in progress")

        with tabs[1]:
            self.add_product()
        with tabs[2]:
            st.write("developement in progress")


if __name__ == "__main__":
    obj = StreamScrape()
    obj.run()
