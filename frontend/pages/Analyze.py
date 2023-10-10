from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import sys
import firebase_admin
from firebase_admin import credentials, firestore
import openai
import re
from utilities import networking
import base64

sys.path.append('/Users/seanstrong/Code/mailmince/frontend/.venv/lib/python3.7/site-packages')
openai.api_key = "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"

def get_firebase_query_from_openai(plaintext):
    """
    Use OpenAI to convert plaintext into a Firebase query.
    """
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt="""We're constructing a Firebase query to retrieve records from the 'record' collection. Please return the code to execute the query. A sample for what the record object looks like is as follows:
      {
        "indexedAt": "2023-10-05T22:43:32.560Z",
        "utcOffset": -7,
        "github": {
            "followers": null,
            "company": null,
            "following": null,
            "handle": null,
            "id": null,
            "blog": null,
            "avatar": null
        },
        "id": "672f4222-0c16-4c77-8b7d-2fffa595b18f",
        "geo": {
            "stateCode": "CA",
            "countryCode": "US",
            "country": "United States",
            "lat": 37.4418834,
            "lng": -122.1430195,
            "state": "California",
            "city": "Palo Alto"
        },
        "twitter": {
            "followers": null,
            "following": null,
            "favorites": null,
            "id": null,
            "handle": null,
            "bio": null,
            "avatar": null,
            "site": null,
            "location": null,
            "statuses": null
        },
        "bio": null,
        "fuzzy": false,
        "timeZone": "America/Los_Angeles",
        "gravatar": {
            "avatar": null,
            "handle": "keith62d8a8c823",
            "urls": [],
            "avatars": []
        },
        "name": {
            "givenName": "Keith",
            "fullName": "Keith Bender",
            "familyName": "Bender"
        },
        "employment": {
            "name": "Pear VC",
            "title": "Partner",
            "subRole": null,
            "seniority": null,
            "domain": "pear.vc",
            "role": null
        },
        "phone": "+1 972-206-7610",
        "linkedin": {
            "handle": "in/keith-bender"
        },
        "facebook": {
            "handle": null
        },
        "inactiveAt": null,
        "avatar": null,
        "email": "keith@pear.vc",
        "site": null,
        "location": "Palo Alto, CA, US",
        "googleplus": {
            "handle": null
        },
        "emailProvider": false
        }
      The query can be for an individual or a list of records. An example for what the appropriate return value looks like for an individual record is as follows:
      where('employment.name', '==', 'Pear VC')

      An example for what the appropriate return value looks like for a list of records is as follows:
      where('employment.name', 'in', ['Pear VC', 'Google'])
      
      Now, convert following provided plaintext a Firebase query that fits the syntax provided over the 'record' collection with the fields above:""" +  plaintext,
      max_tokens=150
    )
    print("Open AI responses: ", response);
    return response.choices[0].text.strip()

def parse_openai_response(response):
    """
    Parse the OpenAI response to extract field, operation, and value.
    Handle both individual and list queries.
    """
    pattern = r"where\('(.+?)',\s*'(.+?)',\s*(\[?.+?\]|'.+?')\)"
    matches = re.findall(pattern, response)
    
    if not matches:
        return None, None, None

    # If there are multiple matches, handle chained queries
    if len(matches) > 1:
        queries = []
        for match in matches:
            field, operation, value = match
            # Convert string representation of list to actual list
            if value.startswith("[") and value.endswith("]"):
                value = eval(value)
            else:
                value = value.strip("'")
            queries.append((field, operation, value))
        return queries
    else:
        field, operation, value = matches[0]
        # Convert string representation of list to actual list
        if value.startswith("[") and value.endswith("]"):
            value = eval(value)
        else:
            value = value.strip("'")
        return [(field, operation, value)]

def execute_firebase_query(queries):
    """
    Construct and execute the Firebase query based on the parsed values.
    """
    db = firestore.client()
    records_ref = db.collection('record')
    
    for field, operation, value in queries:
        records_ref = records_ref.where(field, operation, value)

    docs = records_ref.stream()
    return [doc.to_dict() for doc in docs]



def main():
    st.title("OpenAI to Firebase Query Converter")

    # Take plaintext input from Streamlit
    plaintext = st.text_area("Enter your plaintext:")

    if st.button("Convert and Execute"):
        # Convert plaintext to Firebase query using OpenAI
        query = get_firebase_query_from_openai(plaintext)
        st.write(f"{query}")

        queries = parse_openai_response(query)
        results = execute_firebase_query(queries)

        # st.write("Query Results:", results)
        df = firebase_response_to_dataframe(results)

        def extract_full_name(x):
            if pd.notnull(x) and isinstance(x, dict) and 'fullName' in x:
                return x['fullName']
            return None

        def extract_employer(x):
            if pd.notnull(x) and isinstance(x, dict) and 'name' in x:
                return x['name']
            return None

        def extract_title(x):
            if pd.notnull(x) and isinstance(x, dict) and 'title' in x:
                return x['title']
            return None

        def extract_linkedin_url(x):
            if pd.notnull(x) and isinstance(x, dict) and 'handle' in x and x['handle'] is not None:
                return 'https://www.linkedin.com/' + x['handle']
            return None

        if not df.empty and 'name' in df.columns:
            if df['name'].apply(type).eq(str).all():
                # If all values are strings, then convert them to dictionaries
                df['name'] = df['name'].apply(eval)

            # Now, you don't need to use eval() anymore since the values are already dictionaries
            df['Full name'] = df['name'].apply(extract_full_name)

        if not df.empty and 'employment' in df.columns:
            df['Employer'] = df['employment'].apply(extract_employer)
            df['Title'] = df['employment'].apply(extract_title)

        if not df.empty and 'linkedin' in df.columns:
            df['LinkedIn URL'] = df['linkedin'].apply(extract_linkedin_url)


        # # Now, you don't need to use eval() anymore since the values are already dictionaries
        # df['Full name'] = df['name'].apply(extract_full_name)
        # df['Employer'] = df['employment'].apply(extract_employer)
        # df['Title'] = df['employment'].apply(extract_title)
        # df['LinkedIn URL'] = df['linkedin'].apply(extract_linkedin_url)

        if not df.empty:
            desired_columns = ['email', 'Full name', 'LinkedIn URL', 'Employer', 'Title', 'location']
            filtered_df = df[desired_columns]


            st.write("Query Results", filtered_df)
            st.markdown(get_table_download_link(filtered_df), unsafe_allow_html=True)
        else:
            st.write("No results found.")





def firebase_response_to_dataframe(docs):
    """
    Convert Firebase response to a pandas DataFrame.
    """
    # Check if the first item in docs is already a dictionary

    if not docs:  # Check if docs is empty
        return pd.DataFrame()  # Return an empty DataFrame

    if isinstance(docs[0], dict):
        return pd.DataFrame(docs)
    else:
        return pd.DataFrame([doc.to_dict() for doc in docs])


def get_table_download_link(df):
    """
    Generate a link to download the DataFrame as a CSV.
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="emails.csv">Download CSV File</a>'
    return href



if __name__ == "__main__":
    main()




# Example usage:
# response_from_openai = "where('employment.name', '==', 'Pear VC')"  # This is just a mock example
# field, operation, value = parse_openai_response(response_from_openai)
# results = execute_firebase_query(field, operation, value)
# st.write(results)