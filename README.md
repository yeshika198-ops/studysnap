# StudySnap AI 📚

StudySnap AI is an AI-powered study assistant designed to help students learn in a simple and interactive way.

## Features

* Ask study questions and get easy-to-understand AI answers
* Upload textbook images and ask questions about them
* Demo Mode for testing without live AI requests
* Send study conversations and notes to email
* Simple Streamlit-based user interface

## Technologies Used

* Python
* Streamlit
* Google Gemini AI
* Gmail SMTP

## Setup

1. Clone this repository.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a file named `.streamlit/secrets.toml`.

4. Add your own credentials:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
GMAIL_ADDRESS = "your_email@gmail.com"
GMAIL_APP_PASSWORD = "your_gmail_app_password"
```

5. Run the application:

```bash
streamlit run app.py
```

## Security

Never upload `.streamlit/secrets.toml` or expose API keys and passwords publicly.

## Project Purpose

The goal of StudySnap AI is to make studying easier by combining AI explanations, image-based learning, and email-based study notes in one application.
