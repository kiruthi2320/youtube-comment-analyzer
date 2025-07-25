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
        background-image: linear-gradient(rgba(255,255,255,0.25), rgba(255,255,255,0.25)), 
                          url("data:image/jpg;base64,{b64_encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        animation: fadeIn 2s ease-in-out;
        opacity:0.75;
    }}
    @keyframes fadeIn {{
        0% {{ opacity: 0; }}
        100% {{ opacity: 1; }}
    }}
    .stApp {{
        background: transparent important;
        padding: 2rem 5rem;
        margin: auto;
        max-width: 1100px;
    }}
    h1, h2, h3 {{
        color: #111827;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
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
    st.markdown("<h1 style='text-align: center; margin-top: -40px; font-size: 3rem;'>🎥 YouTube Comment Analyzer</h1>", unsafe_allow_html=True)

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
# Session defaults
for key in ["show_result", "comments", "video_url", "channel_name"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "channel_name" else False

if not st.session_state.show_result:
    st.write("Paste a **YouTube video URL** to fetch comments and analyze popular words, emojis, and sentiment.")

    video_url = st.text_input("Enter YouTube Video URL:")
    channel_input = st.text_input("Enter Channel Name (Optional):")

    if video_url:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.warning("⚠️ Invalid YouTube URL.")
        else:
            st.session_state.video_url = video_url
            st.session_state.channel_name = channel_input.strip()

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
                        st.session_state.show_result = True
                        st.rerun()
                    else:
                        st.error("😕 No comments found.")

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

    # ✅ Show channel info
    st.markdown("## 📺 Channel Info")
    if st.session_state.channel_name:
        st.markdown(f"**🎬 Channel Name:** `{st.session_state.channel_name}`")

    tab1, tab2 = st.tabs(["📋 Summary", "🔍 Detailed View"])

    with tab1:
        st.subheader("💬 Sentiment Breakdown:")
        for s, c in sentiment_counts.items():
            st.write(f"**{s}**: {c} comments")

        st.subheader("📊 Sentiment Distribution (Hover to Explore):")
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
        for key in ["show_result", "video_url", "comments", "channel_name"]:
            st.session_state[key] = "" if isinstance(st.session_state[key], str) else False
        st.rerun()
