import streamlit as st
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from textblob import TextBlob
import re
from collections import Counter
import emoji
import plotly.express as px
import base64

# ----------------- 🎨 Background Style ---------------- #
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
        b64_encoded = base64.b64encode(data).decode()

    css = f"""
    <style>
    body {{
        background: url("data:image/png;base64,{b64_encoded}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }}

    .stApp {{
        background-color: rgba(0, 0, 0, 0.5);
        padding: 4rem 2rem;
        border-radius: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        max-width: 900px;
        margin: auto;
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.5);
    }}

    h1, h2, h3, p, label {{
        color: white !important;
        text-align: center;
    }}

    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.1);
        color: black;
        border: 1px solid #ccc;
        border-radius: 10px;
    }}

    .stButton > button {{
        background-color: #2563eb;
        color: black;
        padding: 0.6rem 1.5rem;
        font-weight: bold;
        font-size: 1rem;
        border: none;
        border-radius: 10px;
        transition: all 0.3s ease;
    }}

    .stButton > button:hover {{
        background-color: #1d4ed8;
        transform: scale(1.05);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown("<h1 style='margin-top: -40px; margin-bottom: 1rem; font-size: 2.8rem;'>🎥 YouTube Comment Analyzer</h1>", unsafe_allow_html=True)

# ----------------- ⚙️ Setup ---------------- #
st.set_page_config(page_title="YouTube Comments Analyzer", layout="centered")
set_background("you.jpg")

# ----------------- 🧠 Helpers ---------------- #
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def fetch_comments(video_id, limit=200):
    downloader = YoutubeCommentDownloader()
    generator = downloader.get_comments_from_url(f"https://www.youtube.com/watch?v={video_id}", sort_by=SORT_BY_POPULAR)
    comments = []
    for count, comment in enumerate(generator):
        comments.append(comment["text"])
        if count >= limit:
            break
    return comments

def clean_text(text):
    text = re.sub(r"http\S+|www.\S+", "", text)
    text = re.sub(r"[^A-Za-z\s]", "", text)
    text = text.lower()
    return text

def extract_emojis(text):
    return [char for char in text if emoji.is_emoji(char)]

def get_sentiment(comment):
    blob = TextBlob(comment)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

# ----------------- 🔁 Page Logic ---------------- #
for key in ["show_result", "comments", "video_url", "channel_name", "go_next"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["show_result", "go_next"] else ""

# ----------------- 📄 Input Page ---------------- #
if not st.session_state.show_result:
    st.markdown("<div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
    video_url = st.text_input("Enter YouTube Video URL:")
    channel_input = st.text_input("Enter Channel Name (Optional):")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Analyze"):
        if not video_url:
            st.warning("⚠️ Please enter a YouTube video URL.")
        else:
            video_id = extract_video_id(video_url)
            if not video_id:
                st.error("❌ Invalid YouTube URL.")
            else:
                with st.spinner("🔍 Fetching comments..."):
                    comments = fetch_comments(video_id)
                    if comments:
                        st.session_state.comments = comments
                        st.session_state.video_url = video_url
                        st.session_state.channel_name = channel_input.strip()
                        st.session_state.show_result = True
                        st.rerun()
                    else:
                        st.error("😕 No comments found.")

# ----------------- ▶️ Transition Page ---------------- #
elif st.session_state.show_result and not st.session_state.go_next:
    st.markdown(f"""
        <div style="
            background-color: #16a34a;
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0 0 10px rgba(0,0,0,0.4);
            margin-bottom: 1rem;
            text-align: center;
        ">
            ✅ Successfully fetched {len(st.session_state.comments)} comments.
        </div>
    """, unsafe_allow_html=True)

    if st.button("➡️ Go to Analysis"):
        st.session_state.go_next = True
        st.rerun()

# ----------------- 📊 Result Page ---------------- #
else:
    comments = st.session_state.comments
    cleaned = [clean_text(c) for c in comments]
    all_text = " ".join(cleaned)
    words = all_text.split()
    word_counts = Counter(words)
    common_words = word_counts.most_common(10)

    emojis = []
    for comment in comments:
        emojis.extend(extract_emojis(comment))
    emoji_counts = Counter(emojis)
    common_emojis = emoji_counts.most_common(10)

    sentiments = [get_sentiment(c) for c in comments]
    sentiment_counts = Counter(sentiments)

    st.markdown("## 📺 Channel Info")
    if st.session_state.channel_name:
        st.markdown(f"**🎬 Channel Name:** `{st.session_state.channel_name}`")

    tab1, tab2 = st.tabs(["📋 Summary", "🔍 Detailed View"])

    with tab1:
        st.markdown("<h3 style='color:#FFD700;'>💬 Sentiment Breakdown:</h3>", unsafe_allow_html=True)

        for s, c in sentiment_counts.items():
            st.write(f"**{s}**: {c} comments")

        st.markdown("<h3 style='color:#FFD700;'>📊 Sentiment Distribution (Hover to Explore):</h3>", unsafe_allow_html=True)
        labels = list(sentiment_counts.keys())
        sizes = list(sentiment_counts.values())

        fig = px.pie(
            names=labels,
            values=sizes,
            title="Sentiment Breakdown of YouTube Comments",
            color=labels,
            color_discrete_map={
                "Positive": "green",
                "Negative": "orange",
                "Neutral": "red"
            },
            hole=0.3
        )

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='white',
            margin=dict(t=80, b=50, l=50, r=50),
            legend=dict(
                orientation="v",
                y=0.5,
                x=1,
                xanchor="left",
                font=dict(color="white", size=13),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                itemwidth=30,
            )
        )

        fig.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Comments: %{value}<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### 📝 Sample Comments")
        for comment in comments[:10]:
            st.markdown(f"👉 {comment}")

        st.markdown("### 🔤 Top 10 Words")
        for word, count in common_words:
            st.markdown(f"**{word}**: {count} times")

        st.markdown("### 😄 Top 10 Emojis")
        if common_emojis:
            for em, count in common_emojis:
                st.markdown(f"{em} — {count} times")
        else:
            st.info("No emojis found.")

    if st.button("🔙 Go Back"):
        for key in ["show_result", "video_url", "comments", "channel_name", "go_next"]:
            st.session_state[key] = "" if isinstance(st.session_state[key], str) else False
        st.rerun()
