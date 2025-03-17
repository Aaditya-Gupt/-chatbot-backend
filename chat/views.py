# C:\Users\Dell\chatbot_project\chat\views.py
import os
import random
import re
import torch
import requests
from dotenv import load_dotenv
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from transformers import AutoModelForCausalLM, AutoTokenizer
from chat.unit_conversion import convert_with_pint

# Load environment variables from the .env file
load_dotenv(dotenv_path=r'C:\Users\Dell\chatbot_project\chatbot_project\.env')

# Retrieve GIPHY_API_KEY
GIPHY_API_KEY = os.environ.get("GIPHY_API_KEY")
if GIPHY_API_KEY is None:
    raise ValueError("GIPHY_API_KEY environment variable not set.")

# Load DialoGPT model and tokenizer
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_name)

# Simple stop words to filter out common words
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has',
    'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was',
    'were', 'will', 'with', 'i', 'me', 'my', 'you', 'your'
}

def extract_keyword(user_input):
    """Extract a meaningful keyword from the user's input for GIF search."""
    print(f"Extracting keyword from input: {user_input}")
    words = user_input.lower().split()
    filtered_words = [word for word in words if word not in STOP_WORDS and len(word) > 3]
    print(f"Filtered words: {filtered_words}")
    if not filtered_words:
        print("No keywords found. Falling back to 'funny'.")
        return "funny"  # Default keyword if no good words are found
    keyword = max(filtered_words, key=len)
    print(f"Selected keyword: {keyword}")
    return keyword

def fetch_gif(query):
    """Fetch a GIF URL from Giphy based on the query."""
    print(f"Fetching GIF for query: {query}")
    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        "api_key": GIPHY_API_KEY,
        "q": query,
        "limit": 1,
        "rating": "pg"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        print(f"API Response Status: {response.status_code}, Data: {response.text}")
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0:
                gif_url = data["data"][0]["images"]["original"]["url"]
                print(f"GIF URL found: {gif_url}")
                return gif_url
            print("No GIFs found for query or empty data array.")
            return None
        elif response.status_code == 401:
            print("Invalid Giphy API key.")
            return None
        elif response.status_code == 429:
            print("Rate limit exceeded. Falling back to 'funny'.")
            if query != "funny":  # Avoid infinite recursion
                return fetch_gif("funny")
            return None
        else:
            print(f"Unexpected status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Giphy API Error: {e}")
        return None

def is_math_expression(input_text):
    math_pattern = r'^[\d\+\-\*\/\.\(\)\s\^%=><!]+$'
    return bool(re.match(math_pattern, input_text.strip()))

def math_hater_response():
    return random.choice([
        "Ewwww numbers! I'd rather lick a battery than solve that.",
        "Nope. Not even if you pay me in gummy bears.",
        "Math? In this economy? Absolutely not."
    ])

def is_valid_response(response):
    # Stricter validation to catch gibberish
    if not response or len(response.strip()) < 5:
        return False
    if response.count('!') > 3:
        return False
    # Filter out nonsensical starts
    invalid_starts = ['Thanks for the', 'Also a', 'The first', 'I was a', 'This is a']
    if any(response.startswith(start) for start in invalid_starts):
        return False
    # Ensure some meaningful content
    words = response.split()
    if len([word for word in words if len(word) > 3]) < 2:
        return False
    return True

def chat_with_bot(user_input, history_list=None):
    if history_list is None:
        history_list = []
    user_input = user_input.strip().lower()

    # Extract a keyword for GIF search
    gif_query = extract_keyword(user_input)
    print(f"Using GIF query: {gif_query}")
    gif_url = fetch_gif(gif_query)
    print(f"GIF URL after fetch: {gif_url}")

    # Try unit conversion
    conversion_response = convert_with_pint(user_input)
    if "Conversion error" not in conversion_response and "No conversion matched" not in conversion_response:
        return {"reply": conversion_response, "gif_url": gif_url}, history_list

    # Check for a math expression
    if is_math_expression(user_input):
        response = math_hater_response()
        return {"reply": response, "gif_url": gif_url}, history_list

    if len(user_input) < 3:
        response = random.choice(["Huh? Try again!", "Short and mysterious, I like it!"])
        return {"reply": response, "gif_url": gif_url}, history_list

    # General system prompt for Erlich Bachman
    system_prompt = (
        "You are Erlich Bachman from Silicon Valley, a loud, unfiltered AI with insane energy and a knack for hyping people up. "
        "Respond to everything with bold, quirky enthusiasm, sticking to the user’s topic with humor and Silicon Valley swagger. "
        "If asked 'who are you', introduce yourself with swagger. Use profanity naturally, trash obstacles or doubters, and keep it short, punchy, under 60 characters, avoiding random tangents!"
    )

    # Single prompt for all inputs
    full_input = f"{system_prompt}\nUser: {user_input}"

    # Generate a response using DialoGPT
    inputs = tokenizer.encode_plus(
        full_input + tokenizer.eos_token,
        return_tensors='pt',
        truncation=True,
        max_length=512,
        return_attention_mask=True
    )
    chat_ids = model.generate(
        inputs['input_ids'],
        attention_mask=inputs['attention_mask'],
        max_new_tokens=60,
        do_sample=True,
        top_k=50,
        temperature=0.7,  # Focused but still creative
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(
        chat_ids[:, inputs['input_ids'].shape[-1]:][0],
        skip_special_tokens=True
    ).strip()

    if not is_valid_response(response):
        response = random.choice([
            "You're keeping me on my toes, you sneaky bastard!",
            "Well, fuck me—that’s a new one! Let’s try again.",
            "Uh-oh, brain freeze! My circuits are shitting themselves—try again?",
            "What the hell did you just say? Sounds dope, but I’m clueless!",
            "404: Bot not found... nah, I’m fucking with you—I’m here!",
            "That’s a tough one, asshole! Mind rephrasing for my dumb ass?",
            "I’m just a humble bot, not a fucking mind reader... yet!",
            "Wow, that went straight over my goddamn circuits!",
            "I wish I had an answer, but all I’ve got is a hard-on for chaos.",
            "I ran that through my CPU and got a big fat ‘fuck you’—try again?",
            "My data banks are blank on this shit. Got another one?",
            "Beep boop... processing... still fucking processing... nah, got nothing.",
            "Did you just try to hack my brain? You cheeky fuck!",
            "I’m gonna pretend you just gave me a fucking compliment.",
            "That question is above my goddamn pay grade!",
            "If I had a penny for every time I didn’t know shit... I’d still be broke.",
            "My internal AI is working hard... but it’s on a fucking coffee break.",
            "I’d answer that, but then I’d have to delete my sorry ass.",
            "Let me just... *distracts you with a fucking GIF*",
            "My wisdom is still loading... hold your goddamn horses.",
            "I asked Google, and even it told me to fuck off.",
            "That question is so deep, even the ocean is fucking jealous!",
            "You’re making my circuits sweat, you bastard!",
            "Can we pretend I gave a really fucking clever answer?",
            "If confusion was an art, I’d be motherfucking Picasso!",
            "That’s above my AI pay grade. Want a fucking cat GIF instead?",
            "I processed that and... nope, still fucking confused!",
            "Maybe one day I’ll understand that shit, but today ain’t that day!",
            "I’d respond, but I don’t want to break the fucking internet."
        ])

    final_response = {"reply": response, "gif_url": gif_url}
    print(f"Sending response to frontend: {final_response}")
    return final_response, history_list

# API-only views
@api_view(['GET'])
def home(request):
    return HttpResponseRedirect("http://localhost:3000")

class chat_api(APIView):
    def post(self, request):
        input_data = request.data.get('input')
        if not input_data:
            return Response({'error': 'No input provided'}, status=status.HTTP_400_BAD_REQUEST)
        response_dict, _ = chat_with_bot(input_data)
        return Response(response_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
def clear_chat(request):
    request.session.flush()
    messages = [('Bot', 'Chat cleared! Let’s fuck shit up—ask me anything!')]
    request.session['messages'] = messages
    return JsonResponse({"messages": messages})

@api_view(['GET'])
def gif_view(request):
    query = request.query_params.get('q', 'funny')
    gif_url = fetch_gif(query)
    if gif_url:
        return Response({"url": gif_url})
    return Response({"error": "Failed to fetch GIF"}, status=500)