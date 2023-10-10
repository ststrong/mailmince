from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import sys
sys.path.append('/Users/seanstrong/Code/mailmince/frontend/.venv/lib/python3.7/site-packages')

# from 'utilities' import networking
#import networking.py from the utilities folder
from utilities import networking


"""
# ✉️ MailMince

Upload a CSV of the mailing list you want to segment. We'll then allow you to:
1. Augment the emails
2. Get analytics on domains, roles, and company types
3. Segment the list & export audiences based on data
4. Send emails to custom lists
"""

def main():
    st.title("CSV Uploader in Streamlit")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file, header=None)
        
        # Display the DataFrame
        st.write(df)

        # Extract the domain from each email
        df['domain'] = df[0].str.extract('@([\w.-]+)')

        # Get unique domains as a list
        domain_counts = df['domain'].value_counts()
        domain_counts_dict = domain_counts.to_dict()
        st.write(domain_counts_dict)

        networking.process_email('pejman@pear.vc')

if __name__ == "__main__":
    main()
