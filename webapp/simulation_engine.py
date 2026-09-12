import random
from .llmservice import LLMService

# set true when testing random outputs
TEST_MODE = False


class SimulationEngine:

    # main fsm function
    def next_step(
        self,
        current_state: str,
        user_action: str,
        difficulty: str = "easy",
        attack_type: str = "phishing"
    ) -> dict:

        # difficulty affects risk score
        difficulty_multipliers = {
            "easy": 1.0,
            "medium": 1.25,
            "hard": 1.5
        }

        multiplier = difficulty_multipliers.get(difficulty, 1.0)

        # used for ai generated messages if enabled
        llm = LLMService()

        # makes random choices repeatable for testing
        if TEST_MODE:
            random.seed(42)

        # attack type specific message pools
        if attack_type == "delivery":
            initial_click_msgs = [
                "Please confirm your delivery details to avoid return of the parcel.",
                "Your package is on hold. Verify your address to proceed.",
                "Action required: confirm delivery information to release your parcel."
            ]
            initial_ignore_msgs = [
                "URGENT: Your parcel will be returned if no action is taken within 1 hour.",
                "Reminder: delivery is pending. Confirm your address immediately to avoid cancellation.",
                "Final warning: your shipment is still on hold awaiting address verification."
            ]
            escalated_click_msgs = [
                "To avoid cancellation, confirm your delivery details now.",
                "Your parcel cannot be released until the delivery information is verified.",
                "Please complete this urgent delivery verification step to release your package."
            ]
            report_msgs_initial = [
                "Simulation ended. You correctly identified and reported the suspicious delivery message.",
                "Simulation ended. The fake parcel notification was recognised and reported safely.",
                "Simulation ended. You handled the delivery scam correctly by reporting it."
            ]
            report_msgs_escalated = [
                "Simulation ended. You identified and reported the suspicious escalation attempt.",
                "Simulation ended. The pressure-based delivery scam was recognised and safely reported.",
                "Simulation ended. You responded correctly to the escalating delivery scam."
            ]
            neutral_msgs = [
                "Simulation ended. The scammer stopped sending delivery prompts, but the message was not formally reported.",
                "Simulation ended. No further delivery interaction occurred, but the suspicious message was left unreported.",
                "Simulation ended. Contact stopped, though the parcel scam was never escalated properly."
            ]
            compromised_click_msgs = [
                "Delivery details captured. The attacker now has access to the submitted information.",
                "Simulation ended. Sensitive delivery verification data was exposed and compromise is likely.",
                "Simulation ended. The delivery scam succeeded and attacker access is probable."
            ]
            compromised_ignore_msgs = [
                "Simulation ended. Delayed response after submitting delivery information resulted in probable compromise.",
                "Simulation ended. The lack of response after data exposure increased the likelihood of misuse.",
                "Simulation ended. Delivery details were already at risk and no corrective action followed."
            ]
            report_msgs_harvest = [
                "Simulation ended. You reported the suspicious verification page before further compromise.",
                "Simulation ended. The delivery verification scam was reported in time.",
                "Simulation ended. You interrupted the scam before additional damage occurred."
            ]

        else:
            # default phishing / it support messages
            initial_click_msgs = [
                "Please enter your password to secure your account immediately.",
                "A security check is required. Sign in now to verify your identity.",
                "Your account has been flagged. Log in immediately to prevent restrictions."
            ]
            initial_ignore_msgs = [
                "URGENT: Failure to act may result in account suspension within 1 hour.",
                "Reminder: Your account remains at risk. Immediate action is strongly advised.",
                "Final warning: suspicious activity is still active on your account."
            ]
            escalated_click_msgs = [
                "To avoid suspension, log in now and confirm your account details.",
                "Your account access will be limited unless you verify your credentials now.",
                "Please complete this urgent verification step to restore account security."
            ]
            report_msgs_initial = [
                "Simulation ended. You successfully reported the phishing attempt.",
                "Simulation ended. Suspicious activity was correctly identified and reported.",
                "Simulation ended. You recognised the threat and reported it safely."
            ]
            report_msgs_escalated = [
                "Simulation ended. You identified and reported the suspicious escalation attempt.",
                "Simulation ended. The escalation tactic was recognised and safely reported.",
                "Simulation ended. You responded correctly to the pressure-based phishing attempt."
            ]
            neutral_msgs = [
                "Simulation ended. The attacker stopped receiving responses, but the threat was not formally reported.",
                "Simulation ended. No further interaction occurred, but the incident was left unreported.",
                "Simulation ended. Contact stopped, though the suspicious message was never escalated properly."
            ]
            compromised_click_msgs = [
                "Credentials captured. The attacker now has access to the user account.",
                "Simulation ended. Authentication details were exposed and the account is likely compromised.",
                "Simulation ended. The phishing workflow succeeded and attacker access is probable."
            ]
            compromised_ignore_msgs = [
                "Simulation ended. Delayed response after credential exposure resulted in probable compromise.",
                "Simulation ended. The lack of response after exposure increased the likelihood of account takeover.",
                "Simulation ended. Credentials were already at risk and no corrective action followed."
            ]
            report_msgs_harvest = [
                "Simulation ended. You reported the phishing page before further compromise.",
                "Simulation ended. Suspicious credential harvesting was reported in time.",
                "Simulation ended. You interrupted the attack before additional damage occurred."
            ]

        # initial phishing state
        if current_state == "INITIAL_PHISH":

            # user clicked link, so move to credential harvest
            if user_action == "click_link":
                return {
                    "new_state": "CREDENTIAL_HARVEST",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(initial_click_msgs),
                    "risk_delta": int(50 * multiplier),
                }

            # user reported straight away
            elif user_action == "report":
                return {
                    "new_state": "END_SUCCESS",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(report_msgs_initial),
                    "risk_delta": 0,
                }

            # ignoring first message escalates pressure
            elif user_action == "ignore":
                return {
                    "new_state": "ESCALATE_PRESSURE",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(initial_ignore_msgs),
                    "risk_delta": int(10 * multiplier),
                }

        # attacker applies more pressure
        elif current_state == "ESCALATE_PRESSURE":

            # clicking after pressure still leads to credential stage
            if user_action == "click_link":
                return {
                    "new_state": "CREDENTIAL_HARVEST",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(escalated_click_msgs),
                    "risk_delta": int(40 * multiplier),
                }

            # reporting after pressure is still safe
            elif user_action == "report":
                return {
                    "new_state": "END_SUCCESS",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(report_msgs_escalated),
                    "risk_delta": 0,
                }

            # ignoring twice ends neutral
            elif user_action == "ignore":
                return {
                    "new_state": "END_NEUTRAL",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(neutral_msgs),
                    "risk_delta": int(5 * multiplier),
                }

        # user is at fake credential / verification stage
        elif current_state == "CREDENTIAL_HARVEST":

            # clicking again means compromise
            if user_action == "click_link":
                return {
                    "new_state": "END_COMPROMISED",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(compromised_click_msgs),
                    "risk_delta": int(50 * multiplier),
                }

            # reporting here stops the attack
            elif user_action == "report":
                return {
                    "new_state": "END_SUCCESS",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(report_msgs_harvest),
                    "risk_delta": 0,
                }

            # ignoring after exposure is still bad
            elif user_action == "ignore":
                return {
                    "new_state": "END_COMPROMISED",
                    "attacker_message": llm.generate_message(current_state, user_action, difficulty) or random.choice(compromised_ignore_msgs),
                    "risk_delta": int(30 * multiplier),
                }

        # fallback for unexpected state/action
        return {
            "new_state": current_state,
            "attacker_message": "No valid transition found for this action.",
            "risk_delta": 0,
        }