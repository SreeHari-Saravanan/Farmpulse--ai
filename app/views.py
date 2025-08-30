import markdown
from django.utils.safestring import mark_safe

# Helper function to clean and convert the AI response to Markdown
def format_ai_response(response_text):
    # Optionally replace or remove unwanted characters (e.g., '*', '#', etc.)
    clean_text = response_text.replace('*', '').replace('#', '')
    
    # Convert the text to markdown for better readability
    html_text = markdown.markdown(clean_text)
    
    # Return as safe HTML to display in Django templates
    return mark_safe(html_text)

import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image
from io import BytesIO
from datetime import datetime
from .models import SessionData
import time

# Configure Google Generative AI with your API key
genai.configure(api_key="AIzaSyD_7a2fRIy-ETQxrl6frtj5-L5xX1dLM-s")


def analyze(request):
    if request.method == 'POST':
        user_input = request.POST.get('message')  # User's text prompt
        image_file = request.FILES.get('image')  # User's image (if any)

        # Track session start time
        start_time = time.time()

        # Create a session data instance to store the interaction
        session_data = SessionData()

        # Handle image file if provided
        if image_file:
            # Read the image file as binary data
            image_binary = image_file.read()
            session_data.image_data = image_binary
            session_data.image_name = image_file.name  # Store original image name

            # If both text and image are provided
            if user_input:
                try:
                    # Load the image from binary data for AI processing
                    img = Image.open(BytesIO(image_binary))
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    # Use the text prompt and image together for diagnosis
                    response = model.generate_content((user_input, img))

                    # Store the text and response in the session data
                    session_data.text_prompt = user_input
                    session_data.ai_response = format_ai_response(response.text)

                    # Calculate session duration
                    session_duration = time.time() - start_time
                    session_data.session_duration = session_duration
                    session_data.save()  # Save session to MongoDB

                    return JsonResponse({'response': session_data.ai_response})

                except Exception as e:
                    return JsonResponse({'error': str(e)})

            else:
                # Image is provided without text prompt
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(('Analyze the disease in this plant or animal', img))

                    # Store response in the session data
                    session_data.ai_response = format_ai_response(response.text)

                    # Calculate session duration
                    session_duration = time.time() - start_time
                    session_data.session_duration = session_duration
                    session_data.save()

                    return JsonResponse({'response': session_data.ai_response})

                except Exception as e:
                    return JsonResponse({'error': str(e)})

        # If only text is provided
        elif user_input:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(user_input)

                # Store text and AI response
                session_data.text_prompt = user_input
                session_data.ai_response = format_ai_response(response.text)

                # Calculate session duration
                session_duration = time.time() - start_time
                session_data.session_duration = session_duration
                session_data.save()

                return JsonResponse({'response': session_data.ai_response})

            except Exception as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Please provide either text or an image.'})

    return render(request, 'upload.html')
