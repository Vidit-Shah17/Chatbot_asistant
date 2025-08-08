
import os
import json
import re
import math
from pathlib import Path


try:
    import sympy as sp
except Exception:
    sp = None

PROJ_DIR = Path(__file__).resolve().parent.parent
FAQ_PATH = PROJ_DIR / "data" / "faqs.json"

def load_faqs():
    try:
        with open(FAQ_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def faq_answer(user_input: str):
    faqs = load_faqs()
    if not faqs:
        return None
    q = user_input.lower()

    for item in faqs:
        qtext = item.get("question", "").lower()
        if qtext and qtext in q:
            return f"FAQ: {item.get('answer')}"

    best, best_score = None, 0
    tokens_input = set(re.findall(r"\w+", q))
    for item in faqs:
        qtext = item.get("question", "").lower()
        tokens_q = set(re.findall(r"\w+", qtext))
        score = len(tokens_input & tokens_q)
        if score > best_score:
            best_score, best = score, item
    if best and best_score > 0:
        return f"FAQ: {best.get('answer')}"
    return None

# ---------------- Math evaluation ----------------
def safe_eval(expression: str):
    expression = expression.strip()
    if not expression:
        raise ValueError("Empty expression")
    
    if sp:
        try:
            expr = sp.sympify(expression)
            val = float(sp.N(expr))
            return val
        except Exception as e:
            raise ValueError(f"Could not parse expression: {e}")
    else:
       
        allowed = re.compile(r'^[0-9\.\+\-\*\/\^\%\(\)eE\s,]+$')
        if not allowed.match(expression):
            raise ValueError("Expression contains invalid characters (install sympy for full support).")
        expression = expression.replace("^", "**")
        try:
            result = eval(expression, {"__builtins__": None}, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"Evaluation error: {e}")

# ---------------- Algebra ----------------
def algebra_solve(user_input: str):
    if not sp:
        return "Algebra solver not available (SymPy not installed). Run: pip install sympy"
    txt = user_input.strip()
    try:
        lower = txt.lower()
        
        if lower.startswith("solve system"):
            body = txt.split(":",1)[1]
            eqs = [e.strip() for e in body.split(";") if e.strip()]
            parsed = []
            syms = set()
            for eq in eqs:
                if "=" not in eq:
                    return "System format error. Use: solve system: x+y=3; x-y=1"
                left,right = eq.split("=",1)
                parsed.append(sp.Eq(sp.sympify(left), sp.sympify(right)))
                syms |= set(sp.sympify(left).free_symbols)
                syms |= set(sp.sympify(right).free_symbols)
            syms = list(syms)
            sol = sp.solve(parsed, syms, dict=True)
            return f"Solution: {sol}"
        
        m = re.search(r"solve\s+(.+?)(?:\s+for\s+([a-zA-Z]\w*))?$", txt, re.IGNORECASE)
        if m:
            eqpart = m.group(1).strip()
            varname = m.group(2)
            if "=" in eqpart:
                left,right = eqpart.split("=",1)
                expr = sp.Eq(sp.sympify(left), sp.sympify(right))
            else:
                expr = sp.sympify(eqpart)
            if varname:
                symbol = sp.Symbol(varname)
                sol = sp.solve(expr, symbol)
            else:
                syms = list(expr.free_symbols) if hasattr(expr, "free_symbols") else []
                if not syms:
                    sol = sp.solve(sp.Eq(expr, 0))
                else:
                    sol = sp.solve(expr, syms[0])
            return f"Solution: {sol}"
    except Exception as e:
        return f"Error solving algebra: {e}"
    return None

# ---------------- Weather calculations ----------------
def dew_point_celsius(t_c: float, rh_percent: float) -> float:
    a = 17.27; b = 237.7
    alpha = ((a * t_c) / (b + t_c)) + math.log(max(rh_percent, 0.0001) / 100.0)
    dp = (b * alpha) / (a - alpha)
    return round(dp, 2)

def heat_index_celsius(t_c: float, rh_percent: float) -> float:
    t_f = t_c * 9/5 + 32
    RH = rh_percent
    hi_f = (-42.379 + 2.04901523*t_f + 10.14333127*RH - 0.22475541*t_f*RH
            - 0.00683783*t_f*t_f - 0.05481717*RH*RH + 0.00122874*t_f*t_f*RH
            + 0.00085282*t_f*RH*RH - 0.00000199*t_f*t_f*RH*RH)
    hi_c = (hi_f - 32) * 5/9
    return round(hi_c, 2)

def wind_chill_celsius(t_c: float, wind_kmh: float) -> float:
    if wind_kmh <= 4.8 or t_c > 10.0:
        return round(t_c, 2)
    v = wind_kmh
    wc = 13.12 + 0.6215*t_c - 11.37*(v**0.16) + 0.3965*t_c*(v**0.16)
    return round(wc, 2)

def feels_like(t_c: float, rh_percent: float, wind_kmh: float) -> str:
    hi = heat_index_celsius(t_c, rh_percent)
    wc = wind_chill_celsius(t_c, wind_kmh)
    dp = dew_point_celsius(t_c, rh_percent)
    if t_c >= 27:
        return f"Heat index: {hi}°C (dew point {dp}°C)"
    if t_c <= 10 and wind_kmh > 4.8:
        return f"Wind chill: {wc}°C (dew point {dp}°C)"
    return f"Feels like: {t_c}°C (dew point {dp}°C)"

def weather_report_interactive(t_c: float, rh: float, wind_kmh: float):
    dp = dew_point_celsius(t_c, rh)
    hi = heat_index_celsius(t_c, rh)
    wc = wind_chill_celsius(t_c, wind_kmh)
    fl = feels_like(t_c, rh, wind_kmh)
    return {
        "temperature_c": round(t_c,2),
        "humidity_percent": round(rh,2),
        "dew_point_c": dp,
        "heat_index_c": hi,
        "wind_chill_c": wc,
        "feels_like": fl
    }

# ---------------- Intent detection & main runner ----------------
def detect_intent(text: str):
    t = text.lower().strip()
    if t in ("help","h","?"):
        return "help"
    if t in ("exit","quit","q"):
        return "exit"
    if any(k in t for k in ["weather","dew point","dewpoint","heat index","wind chill","feels like"]):
        return "weather"
    if t.startswith("solve"):
        return "algebra"
    if re.match(r"^[\d\.\s\+\-\*\/\^\%\(\)eE,]+$", t) or any(sym in t for sym in ["+", "-", "*", "/", "sqrt", "sin", "cos", "^"]):
        return "math"
    if any(word in t for word in ["support","price","refund","contact","hours","password","how to"]):
        return "faq"
    return "unknown"

def run_agent(user_input: str):
    """
    Return a string or simple JSON-able dict for weather.
    """
    if not user_input or not str(user_input).strip():
        return "Please enter a question."
    intent = detect_intent(user_input)
    if intent == "help":
        return ("Supported: math expressions (e.g. 12/4+3), algebra (solve x+5=10), "
                "weather calculations (type 'weather' and then provide numbers), and FAQ questions.")
    if intent == "math":
        try:
            val = safe_eval(user_input)
            return f"The answer is {val}"
        except Exception as e:
            return f"Could not evaluate expression: {e}"
    if intent == "algebra":
        return algebra_solve(user_input)
    if intent == "weather":
      
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_input)
        if len(nums) >= 3:
            t_c = float(nums[0]); rh = float(nums[1]); wind = float(nums[2])
            rep = weather_report_interactive(t_c, rh, wind)
         
            s = (f"Temperature: {rep['temperature_c']}°C\n"
                 f"Relative Humidity: {rep['humidity_percent']}%\n"
                 f"Dew Point: {rep['dew_point_c']}°C\n"
                 f"Heat Index (approx): {rep['heat_index_c']}°C\n"
                 f"Wind Chill (approx): {rep['wind_chill_c']}°C\n"
                 f"{rep['feels_like']}")
            return s
        else:
         
            return ("Weather tool needs numbers: temperature (°C), humidity (%) and wind speed (km/h). "
                    "Example: 'weather 32 65 8' (means 32°C, 65% humidity, 8 km/h wind).")
  
    faqr = faq_answer(user_input)
    if faqr:
        return faqr
   
    try:
        val = safe_eval(user_input)
        return f"The answer is {val}"
    except Exception:
        pass
    out = algebra_solve(user_input)
    if out:
        return out
    faqr = faq_answer(user_input)
    if faqr:
        return faqr
    return "Sorry, I didn't understand that. Type 'help' for examples."
