# ErlichBot 🎤

A full-stack chatbot that responds like **Erlich Bachman** from HBO's *Silicon Valley* — complete with GIF responses to match the attitude.

## What it does
- Chats with you in Erlich Bachman's signature style — arrogant, verbose, and oddly motivational
- Fetches relevant GIFs via the **GIPHY API** to go along with responses
- Powered by **DialoGPT** for conversational AI on the backend

## Tech Stack
| Layer | Tech |
|-------|------|
| Backend | Django (Python) |
| Frontend | Next.js (JavaScript) |
| AI Model | DialoGPT |
| GIF API | GIPHY API |

## Project Structure
This project is split into two repos:
- [`-chatbot-backend`](https://github.com/Aaditya-Gupt/-chatbot-backend) — Django REST API (this repo)
- [`chatbot-frontend`](https://github.com/Aaditya-Gupt/chatbot-frontend) — Next.js frontend

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- GIPHY API key ([get one free here](https://developers.giphy.com/))

### Backend Setup
```bash
# Clone the backend repo
git clone https://github.com/Aaditya-Gupt/-chatbot-backend.git
cd -chatbot-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your GIPHY API key in settings or .env
GIPHY_API_KEY=your_key_here

# Run the server
python manage.py runserver
```

### Frontend Setup
```bash
# Clone the frontend repo
git clone https://github.com/Aaditya-Gupt/chatbot-frontend.git
cd chatbot-frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```



## Author
**Aaditya Gupta** — [GitHub](https://github.com/Aaditya-Gupt) · [LinkedIn](https://www.linkedin.com/in/aaditya-gupta-5452aa225/)
