import streamlit as st
import pytesseract
import cv2
import pandas as pd
import tempfile
import re
from datetime import datetime
from PIL import Image
import os

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Change for your OS

# Extract relevant fields from OCR text
def extract_data(text):
    text = text.replace('\n', ' ').replace('$', '')
    def get(pattern): return re.search(pattern, text).group(1) if re.search(pattern, text) else None

    return {
        'Date Scraped': datetime.today().strftime('%Y-%m-%d'),
        'Ticker': get(r'View\s([A-Z]+)'),
        'Option Type': get(r'([A-Z]+ \$\d+ Call)'),
        'Strike Price': get(r'\$?(\d+\.\d+)\sCall'),
        'Contracts': get(r'Contracts\s\+?(\d+)'),
        'Cost When Added': get(r'Cost when added\s(\d+\.\d+)'),
        'Current Option Price': get(r'Current price\s(\d+\.\d+)'),
        'Market Value': get(r'Market value\s(\d+\.\d+)'),
        'Date Added': get(r'Date added\s(\d+/\d+)'),
        'Expiration Date': get(r'Expiration date\s(\d+/\d+)'),
        'Breakeven Price': get(r'breakeven price\s(\d+\.\d+)'),
        'Current XYZ Price': get(r'Current XYZ price\s(\d+\.\d+)'),
        'Today Return ($)': get(r"Today's return\s\+?(\d+\.\d+)"),
        'Today Return (%)': get(r"\+?\d+\.\d+\s\(\+?([\d,\.]+)%\)"),
    }

# Main Streamlit App
st.title("Options Watchlist Tracker")

uploaded_file = st.file_uploader("Upload Screenshot", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Screenshot", use_column_width=True)

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        img_path = tmp_file.name

    image = cv2.imread(img_path)
    text = pytesseract.image_to_string(image)
    data = extract_data(text)

    if data['Ticker']:
        df = pd.DataFrame([data])

        if not os.path.exists("watchlist.csv"):
            df.to_csv("watchlist.csv", index=False)
        else:
            df.to_csv("watchlist.csv", mode='a', index=False, header=False)

        st.success("Parsed and saved successfully!")
        st.dataframe(df)
    else:
        st.error("Failed to parse. Please make sure the screenshot format is supported.")
