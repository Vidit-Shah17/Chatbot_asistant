# chatbot/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, logging
from .agent import run_agent

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'chatbot/chat.html')

@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        body = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
        message = body.get('message', '').strip()
        logger.info("chat_api: incoming message: %s", message)
        if not message:
            return JsonResponse({'error': 'Empty message'}, status=400)
        response = run_agent(message)
        logger.info("chat_api: response: %s", response)
        return JsonResponse({'response': response})
    except Exception as e:
        logger.exception("chat_api exception")
        # ALWAYS return JSON (avoid Django debug HTML page being sent to frontend)
        return JsonResponse({'error': 'Internal server error', 'details': str(e)}, status=500)
