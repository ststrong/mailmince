## MinceMail

Mincemail is an experiment in email (a) augmentation, (b) segmentation, and (c) querying. The core question this project was trying to solve was how much latent info is in a mailing list and how can it be better utilized. Turns out, a lot!

The app works via taking in emails individually or over CSV, enriching via the Clearbit API, and then allowing for plaintext queries over the set of emails. It uses a Firebase backend.

A live demo can be accessed at https://mincemail.streamlit.app/, but is only partially functional due to rate limiting with Clearbit's API and expired auth with OpenAIs API.
