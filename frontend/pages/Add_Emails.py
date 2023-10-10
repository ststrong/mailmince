from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import sys
sys.path.append('/Users/seanstrong/Code/mailmince/frontend/.venv/lib/python3.7/site-packages')

from utilities import networking


def main():
    ind_upload()
    bulk_upload()



def ind_upload():
    st.subheader("Add emails individually:")
    with st.form(key="email_form"):
        # Create an input box for the email
        email = st.text_input(label="Enter your email:")

        # Create a submit button for the form
        submit_button = st.form_submit_button(label="Submit")

        # Check if the form has been submitted
        if submit_button:
            if email:  # Check if email input is not empty
                st.write(f"You entered: {email}")
                ###
                email_data = networking.process_email(email)
                if email_data:
                    st.json(email_data)  # Display the email data as JSON
                else:
                    st.warning("Failed to process the email.")
                ####
            else:
                st.warning("Please enter an email.")

def bulk_upload(limit=50):
    st.subheader("Add emails in bulk:")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)

        # Check if there's an 'email' field in the CSV
        email_field = None
        for col in df.columns:
            if 'email' in col.lower():
                email_field = col
                break

        # If no email field is found, assume the entire CSV is a list of emails
        if email_field is None:
            df.columns = ['Original Email']
            email_field = 'Original Email'

        # Define the count N
        N = limit  # or any other value you want

        # Create a new DataFrame to store original and processed emails
        processed_df = df[[email_field]].iloc[:N].copy()
        processed_df.columns = ['Original Email']

        # Apply the process_email() function on each email up to count N
        processed_df['Processed Email'] = processed_df['Original Email'].apply(networking.process_email)

        # Display the DataFrame with original and processed emails in Streamlit
        st.write(processed_df)


if __name__ == "__main__":
    main()
