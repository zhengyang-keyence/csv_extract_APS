import io
import string

import pandas as pd
import streamlit as st


def column_number(letter):
    """Convert a column letter (A, B, ..., AA) to a zero-based number."""
    result = 0
    for char in letter.upper():
        if char not in string.ascii_uppercase:
            raise ValueError(f"Invalid column letter: {letter}")
        result = result * 26 + ord(char) - ord("A") + 1
    return result - 1


def parse_column_letters(text):
    """Parse letters separated by commas, spaces, or semicolons."""
    parts = text.replace(";", ",").replace(" ", ",").split(",")
    return [part.strip().upper() for part in parts if part.strip()]


st.set_page_config(page_title="CSV Extractor", page_icon="📄")
st.title("CSV Extractor")
st.write("Upload a CSV, select the rows and columns you need, then download the result.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    try:
        # Assumes the first line contains column headers.
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read this CSV file: {error}")
        st.stop()

    if df.empty and len(df.columns) == 0:
        st.error("The uploaded file appears to be empty.")
        st.stop()

    st.subheader("File preview")
    st.caption(f"{len(df):,} data rows · {len(df.columns):,} columns")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Extraction settings")

    col1, col2 = st.columns(2)

    with col1:
        start_col = st.text_input(
            "First column",
            value="A",
            help="Enter a column letter, such as A or C.",
        )
        start_row = st.number_input(
            "First data row",
            min_value=1,
            value=1,
            step=1,
            help="Data rows are numbered from 1; the header row is not counted.",
        )

    with col2:
        default_last_col = ""
        # Convert the final DataFrame column number to a letter.
        n = len(df.columns)
        while n:
            n, remainder = divmod(n - 1, 26)
            default_last_col = chr(65 + remainder) + default_last_col

        end_col = st.text_input("Last column", value=default_last_col or "A")
        end_row = st.number_input(
            "Last data row",
            min_value=1,
            value=max(1, len(df)),
            step=1,
        )

    skip_text = st.text_input(
        "Columns to skip (optional)",
        placeholder="For example: C, F, H",
        help="Enter column letters separated by commas.",
    )

    if st.button("Extract data", type="primary"):
        try:
            first_col_index = column_number(start_col.strip())
            last_col_index = column_number(end_col.strip())

            if first_col_index > last_col_index:
                st.error("The first column must come before or equal the last column.")
                st.stop()

            if last_col_index >= len(df.columns):
                st.error(f"This file has {len(df.columns)} columns.")
                st.stop()

            if start_row > end_row:
                st.error("The first data row must be less than or equal to the last data row.")
                st.stop()

            skipped_letters = parse_column_letters(skip_text)
            skipped_indices = {column_number(letter) for letter in skipped_letters}

            selected_indices = [
                index
                for index in range(first_col_index, last_col_index + 1)
                if index not in skipped_indices
            ]

            if not selected_indices:
                st.error("All columns in the selected range were skipped.")
                st.stop()

            # User-facing data rows are 1-based; pandas row positions are 0-based.
            extracted = df.iloc[start_row - 1 : end_row, selected_indices]

            st.subheader("Extracted data")
            st.caption(f"{len(extracted):,} rows · {len(extracted.columns):,} columns")
            st.dataframe(extracted.head(20), use_container_width=True)

            output = io.BytesIO()
            extracted.to_csv(output, index=False, encoding="utf-8-sig")
            output.seek(0)

            st.download_button(
                "Download extracted CSV",
                data=output,
                file_name="extracted_data.csv",
                mime="text/csv",
            )

        except ValueError as error:
            st.error(str(error))
