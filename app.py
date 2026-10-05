import time
import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE


st.set_page_config(
    page_title="StudySnap AI",
    page_icon="📚"
)


# -----------------------------
# Gemini Client
# -----------------------------

@st.cache_resource
def get_gemini_client():

    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


gemini_client = get_gemini_client()

MODEL_NAME = "gemini-3.8-flash"

DEMO_MODE = st.toggle(
    "🎓 Demo Mode",
    value=False
)


# -----------------------------
# Demo Answer
# -----------------------------

def get_demo_answer(question):

    question = question.lower()

    if "gatt" in question:

        return (
            "GATT stands for General Agreement on Tariffs and Trade.\n\n"
            "It is an international agreement that promotes free trade "
            "between countries by reducing trade barriers such as tariffs.\n\n"
            "Example: Countries agree to reduce import duties so goods "
            "can be traded more easily."
        )

    elif "separate legal entity" in question:

        return (
            "A separate legal entity means that a company has its own "
            "legal identity, separate from its owners.\n\n"
            "The company can own property, enter into contracts, sue, "
            "and be sued in its own name.\n\n"
            "Example: A company can borrow money in the company's name, "
            "not in the personal name of its shareholders."
        )

    else:

        return (
            "📚 Demo Mode Answer\n\n"
            "This is a sample StudySnap AI answer for demonstration.\n\n"
            "In the live version, Gemini AI will analyze your question "
            "and provide a personalized academic explanation."
        )


# -----------------------------
# Gmail
# -----------------------------

def send_email(to_address, subject, body):

    message = MIMEText(body)

    message["Subject"] = subject
    message["From"] = st.secrets["GMAIL_ADDRESS"]
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

        server.login(
            st.secrets["GMAIL_ADDRESS"],
            st.secrets["GMAIL_APP_PASSWORD"]
        )

        server.send_message(message)


# -----------------------------
# Chat Session
# -----------------------------

if "chat" not in st.session_state:

    st.session_state.chat = gemini_client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        )
    )


# -----------------------------
# Messages
# -----------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# -----------------------------
# Page
# -----------------------------

st.title("📚 StudySnap AI")

st.subheader(
    "Your Personal AI Study Assistant"
)

st.write(
    "Ask questions, upload textbook pages, and learn difficult topics in simple language."
)

st.divider()


# -----------------------------
# Welcome Message
# -----------------------------

if not st.session_state.messages:

    welcome = WELCOME_MESSAGE_TEMPLATE.format(
        name="Student"
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": welcome
        }
    )


# -----------------------------
# Display Messages
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message.get("image"):

            st.image(message["image"])

        st.write(message["content"])


# -----------------------------
# Chat Input + Photo Upload
# -----------------------------

user_input = st.chat_input(
    "Ask your study question or upload a textbook photo...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"]
)


if user_input:

    user_text = user_input.text

    uploaded_file = None

    if user_input.files:

        uploaded_file = user_input.files[0]


    # -------------------------
    # Show User Message
    # -------------------------

    with st.chat_message("user"):

        if uploaded_file:

            st.image(uploaded_file)

        if user_text:

            st.write(user_text)


    # -------------------------
    # Save User Message
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": (
                user_text
                if user_text
                else "Uploaded a photo."
            ),
            "image": uploaded_file
        }
    )


    # -------------------------
    # Assistant Response
    # -------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                # -------------------------
                # Demo Mode
                # -------------------------

                if DEMO_MODE:

                    answer = get_demo_answer(
                        user_text if user_text else "uploaded photo"
                    )


                # -------------------------
                # Real Gemini Mode
                # -------------------------

                else:

                    # Prepare message

                    if uploaded_file:

                        photo_bytes = uploaded_file.getvalue()

                        photo_part = types.Part.from_bytes(
                            data=photo_bytes,
                            mime_type=uploaded_file.type
                        )

                        if user_text:

                            message_to_send = [
                                photo_part,
                                user_text
                            ]

                        else:

                            message_to_send = [
                                photo_part,
                                "Explain this image in simple language."
                            ]

                    else:

                        message_to_send = user_text


                    # Try Gemini

                    response = None

                    for attempt in range(3):

                        try:

                            response = (
                                st.session_state.chat.send_message(
                                    message_to_send
                                )
                            )

                            break

                        except Exception as error:

                            error_text = str(error)

                            if "503" in error_text:

                                if attempt < 2:

                                    time.sleep(3)

                                else:

                                    raise error

                            else:

                                raise error


                    answer = response.text


                # -------------------------
                # Show Answer
                # -------------------------

                st.write(answer)


                # -------------------------
                # Save Answer
                # -------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


            except Exception as error:

                error_text = str(error)

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                    st.warning(
                        "⚠️ Gemini's daily AI limit has been reached. "
                        "Please turn ON Demo Mode to continue the demonstration."
                    )

                elif "503" in error_text:

                    st.warning(
                        "⚠️ Gemini is temporarily busy. "
                        "Please try again in a few minutes."
                    )

                else:

                    st.error(
                        f"Something went wrong: {error}"
                    )


# =====================================================
# EMAIL STUDY SUMMARY
# =====================================================

st.divider()

st.subheader("📧 Save Your Study Notes")

st.write(
    "Save your questions and AI answers for later revision."
)


# -----------------------------
# Email Address
# -----------------------------

recipient_email = st.text_input(
    "📧 Your email address",
    placeholder="example@gmail.com"
)


# -----------------------------
# Send Summary Button
# -----------------------------

if st.button(
    "📤 Send My Study Notes",
    use_container_width=True
):

    if not recipient_email:

        st.warning(
            "Please enter your email address."
        )

    elif "@" not in recipient_email:

        st.warning(
            "Please enter a valid email address."
        )

    elif len(st.session_state.messages) <= 1:

        st.warning(
            "Please ask at least one study question before sending a summary."
        )

    else:

        with st.spinner(
            "Preparing your study summary..."
        ):

            try:

                # -------------------------
                # Build Email Content
                # -------------------------

                email_body = """
StudySnap AI
Your Study Conversation
========================

"""

                for message in st.session_state.messages:

                    role = message["role"]

                    content = message["content"]

                    if role == "user":

                        email_body += (
                            "\n\nSTUDENT:\n"
                            + content
                            + "\n"
                        )

                    elif role == "assistant":

                        email_body += (
                            "\nSTUDYSNAP AI:\n"
                            + content
                            + "\n"
                        )


                # -------------------------
                # Send Email
                # -------------------------

                send_email(
                    recipient_email,
                    "📚 StudySnap AI - Your Study Notes",
                    email_body
                )


                st.success(
                    "✅ Your study notes have been sent to your email!"
                )


            except Exception as error:

                st.error(
                    f"Unable to send email: {error}"
                )