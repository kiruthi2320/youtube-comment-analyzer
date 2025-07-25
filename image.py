# image.py
import streamlit as st
import base64

def set_background(image_file: str):
    with open(image_file, "rb") as f:
        data = f.read()
        b64_encoded = base64.b64encode(data).decode()

    css = f"""
    <style>
    body {{
        background-image: url("data:image/png;base64,{b64_encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        margin: 0;
        padding: 0;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
    }}

    h1, h2, h3 {{
        color: #111827;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        font-size: 2rem;
    }}

    .stTextInput > div > input {{
        background-color: #111827;         /* darker gray background */
        border: 1px solid #374151;         /* defined dark border */
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-size: 1.1rem;
        color: black;                    /* light text color */
        font-weight: 500;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
        transition: all 0.2s ease-in-out;
    }}

    .stTextInput > div > input:focus {{
        border-color: black;             /* blue on focus */
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
        outline: none;
    }}

    .stButton > button {{
        background-color: #2563eb;
        color: white;
        padding: 0.65rem 1.2rem;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease;
    }}

    .stButton > button:hover {{
        background-color: #1d4ed8;
        transform: scale(1.04);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
