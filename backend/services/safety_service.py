from backend.services.ai_service import call_gemini, AIServiceError, AIConfigurationError
from backend.database.models import SafetyPlanModel

VALID_SITUATIONS = [
    "I'm going somewhere",
    "I need to get home safely",
    "I feel uncomfortable",
    "I want to prepare in advance",
    "Something else"
]

SYSTEM_SAFETY_PROMPT = """You are an empathetic, discreet personal safety planning assistant for Chroma Blend.
Your goal is to provide practical, calm, non-confrontational, actionable step-by-step guidance tailored to the user's specific context.

Guidelines:
1. Tone: Warm, grounded, reassuring, clear, and objective. Avoid clinical jargon, panic-inducing phrases, or aggressive confrontation.
2. Structure:
   - Immediate Step: What to do right now (breathing, situational awareness, checking surroundings).
   - Check-in & Transit: Discrete check-in cadence with a trusted contact, transit choices (well-lit routes, licensed cabs, public spaces).
   - Discreet Signals: Pre-agreed code words, polite excuses to exit safely without escalating tension.
   - Resource Check: Battery level, transportation backup, emergency numbers.
3. Clarity: Use concise bullet points that are easy to skim under stress.
4. Boundaries: Do not claim this plan guarantees physical safety. Include a gentle closing reminder that in an acute emergency, calling local emergency services (e.g. 911/112) is the safest action.
"""

def generate_and_save_plan(user_id: int, situation: str, input_details: str = ''):
    """
    Generate a personalized safety plan using Gemini and store it in SQLite.
    """
    if not situation:
        raise ValueError("A situation must be selected.")
    
    user_prompt = f"""Situation: {situation}
Context / Details provided by user:
{input_details if input_details.strip() else 'No additional details provided.'}

Please generate a practical, discrete, calm safety plan following the system instructions."""

    plan_text = call_gemini(user_prompt, system_instruction=SYSTEM_SAFETY_PROMPT)
    
    # Save generated plan to database under user_id
    saved_record = SafetyPlanModel.create(
        user_id=user_id,
        situation=situation,
        input_details=input_details,
        generated_plan=plan_text
    )
    return saved_record
