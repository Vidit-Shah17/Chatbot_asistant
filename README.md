# HelpMate — LLM Agent Chatbot (Django + LangChain)

## Features
- Calculator
- Algebra solver (SymPy)
- FAQ (customer service)
- Weather (OpenWeatherMap)
- Wikipedia lookups (LangChain)

## Run locally (Windows)
1. Activate venv: `.\venv\Scripts\Activate.ps1`
2. Install requirements: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Run dev server: `python manage.py runserver`
5. Open: http://127.0.0.1:8000

Demo prompts:
- `What is Alan Turing?`
- `Calculate 23 * 47`
- `Solve x^2 - 4 = 0 for x`
- `What's the weather in Mumbai?`
- `How can I reset my password?`
