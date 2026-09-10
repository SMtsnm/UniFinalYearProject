import os
from openai import OpenAI

# get API key from environment, this done for security reasons
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# toggle AI usage (can turn off easily)
USE_AI = False


class LLMService:

    # generate attacker message using AI
    def generate_message(self, current_state: str, user_action: str, difficulty: str) -> str | None:

        # if AI disabled, just skip
        if not USE_AI:
            return None

        try:
            # build prompt based on current sim state
            prompt = f"""
            You are simulating a cyber attacker performing a phishing attack.
            
            State: {current_state}
            Action: {user_action}
            Difficulty: {difficulty}
            
            Generate a short realistic phishing message (1–2 sentences).
            Do NOT mention simulation.
            """

            # call openai (short timeout so it doesn't hang)
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                timeout=2  # hard cap
            )

            # return clean text
            return response.output_text.strip()

        except Exception as e:
            # if AI fails, just use fallback (don't crash)
            print("LLM FAIL (fallback used):", str(e))
            return None