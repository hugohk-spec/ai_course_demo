import streamlit as st
import os
import json
import random
import textwrap
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
import re

STATE_FILE = ".fortune_state.json"
FORTUNES_FILE = "fortunes.txt"
COOLDOWN_HOURS = 12

load_dotenv()
API_KEY = os.getenv("API_KEY")
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://api.poe.com/v1",
)


def load_fortunes(path):
    """Load fortunes from a file.

    Each line may be either:
      CATEGORY|fortune text
    where CATEGORY is one of: BIG, SMALL, BAD
    If no category is provided the fortune is treated as SMALL.

    Returns a list of dicts: {"category": "BIG|SMALL|BAD", "text": "..."}
    """
    if not os.path.exists(path):
        return []
    fortunes = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if "|" in line:
                cat, txt = line.split("|", 1)
                cat = cat.strip().upper()
                txt = txt.strip()
                if cat not in ("BIG", "SMALL", "BAD"):
                    cat = "SMALL"
            else:
                cat = "SMALL"
                txt = line
            fortunes.append({"category": cat, "text": txt})
    return fortunes


def load_state(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(path, state):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def can_open(last_iso, cooldown_hours):
    if not last_iso:
        return True, None
    try:
        last = datetime.fromisoformat(last_iso)
    except Exception:
        return True, None
    next_available = last + timedelta(hours=cooldown_hours)
    now = datetime.utcnow()
    return (now >= next_available), next_available


def can_roll(last_iso, cooldown_minutes):
    if not last_iso:
        return True, None
    try:
        last = datetime.fromisoformat(last_iso)
    except Exception:
        return True, None
    next_available = last + timedelta(minutes=cooldown_minutes)
    now = datetime.utcnow()
    return (now >= next_available), next_available


def format_timedelta(td):
    total = int(td.total_seconds())
    if total <= 0:
        return "0s"
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def main():
    st.set_page_config(page_title="Luck Tests", page_icon="🍀")
    
    # Add a chill background
    st.markdown("""
    <style>
    body {
        background: #f0f0f0;
        color: black;
    }
    .stApp {
        background: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    Test = st.sidebar.radio("Choose a luck test", ["Daily Luck Assessment", "Fortune Cookie", "Dice Roll", "Coin Flip Streak", "Custom Luck Test"])

    if Test == "Daily Luck Assessment":
        st.title("AI's Daily Luck Test---How Lucky Are You Today? 🍀")

        st.write("Please describe three different things that happened to you today:")
        thing1 = st.text_area("Thing 1:", height=100)
        thing2 = st.text_area("Thing 2:", height=100)
        thing3 = st.text_area("Thing 3:", height=100)
        
        user_input = f"Thing 1: {thing1}\nThing 2: {thing2}\nThing 3: {thing3}"
        
        if st.button("Analyze My Luck"):
            if thing1.strip() and thing2.strip() and thing3.strip():
                with st.spinner("Analyzing your luck..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a luck analyst. Based on the user's description of their day, determine their luck level on a scale of 1-100. Output in this format: 'Luck Level: X/100\n\nComment: [your comment]\n\nSuggestion: [what to do later]' Keep the response friendly and encouraging."},
                                {"role": "user", "content": f"Events of my day: {user_input}"}
                            ]
                        )
                        ai_response = response.choices[0].message.content
                        parts = ai_response.split('\n\n')
                        if len(parts) >= 3:
                            luck_line = parts[0]
                            comment = parts[1]
                            suggestion = parts[2]
                            match = re.search(r'Luck Level: (\d+)/100', luck_line)
                            if match:
                                luck = int(match.group(1))
                                st.write(f"Your Luck Meter: {luck}/100")
                                st.progress(luck / 100)
                                if luck <= 20:
                                    desc = "Very Unlucky 😞"
                                elif luck <= 40:
                                    desc = "Unlucky 😕"
                                elif luck <= 60:
                                    desc = "Average Luck 😐"
                                elif luck <= 80:
                                    desc = "Lucky 😊"
                                else:
                                    desc = "Very Lucky 😄"
                                st.write(f"Luck Level: {desc}")
                            st.write(comment)
                            st.write(suggestion)
                        else:
                            st.write(ai_response)
                    except Exception as e:
                        st.error(f"Error analyzing luck: {str(e)}")
            else:
                st.warning("Please fill in all three things.")

    elif Test == "Fortune Cookie":
        st.title("AI Fortune Cookie 🥠")

        fortunes = load_fortunes(FORTUNES_FILE)
        if not fortunes:
            st.error(f"No fortunes found. Please add fortunes to {FORTUNES_FILE}.")
            return

        state = load_state(STATE_FILE)
        last_iso = state.get("last_shown")
        available, next_time = can_open(last_iso, COOLDOWN_HOURS)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Click the cookie to get a random AI-generated fortune. You can open one every 12 hours.")
        # Use session state to surface cooldown warnings below the main area
        if "unavailable_warning" not in st.session_state:
            st.session_state.unavailable_warning = None
        if "current_fortune" not in st.session_state:
            st.session_state.current_fortune = None

        with col2:
            button_col, countdown_col = st.columns([1, 1])
            with button_col:
                if st.button("Open a fortune cookie 🥠"):
                    if not available:
                        # set a flag so the warning is rendered below the divider
                        st.session_state.unavailable_warning = f"You already opened a fortune. Next available: {next_time} UTC"
                    else:
                        choice = random.choice(fortunes)
                        cat = choice.get("category", "SMALL")
                        text = choice.get("text", "")
                        # Display according to category
                        if cat == "BIG":
                            wrapped = textwrap.wrap(f"**BIG FORTUNE:** {text}", width=60)
                            display_text = '\n'.join(wrapped[:2])
                            st.write(display_text)
                        elif cat == "SMALL":
                            wrapped = textwrap.wrap(f"**Small fortune:** {text}", width=60)
                            display_text = '\n'.join(wrapped[:2])
                            st.write(display_text)
                        else:  # BAD
                            wrapped = textwrap.wrap(f"**Bad luck:** {text}", width=60)
                            display_text = '\n'.join(wrapped[:2])
                            st.write(display_text)
                        state["last_shown"] = datetime.utcnow().isoformat()
                        state["last_fortune"] = {"category": cat, "text": text}
                        save_state(STATE_FILE, state)
                        # clear any previous unavailable warning
                        st.session_state.unavailable_warning = None
                        st.session_state.current_fortune = {"category": cat, "text": text}
            with countdown_col:
                if not available and next_time:
                    now = datetime.utcnow()
                    remaining = next_time - now
                    if remaining.total_seconds() > 0:
                        st.write(f"Time until next: {format_timedelta(remaining)}")
                        if st.button("Refresh"):
                            st.rerun()
                    else:
                        st.write("Ready!")

        st.markdown("---")
        # If the user tried to open while on cooldown, show warning here so it doesn't overlap
        if st.session_state.get("unavailable_warning"):
            st.warning(st.session_state.unavailable_warning)

        # Display current fortune if it exists
        if st.session_state.get("current_fortune"):
            cat = st.session_state.current_fortune["category"]
            text = st.session_state.current_fortune["text"]
            if cat == "BIG":
                wrapped = textwrap.wrap(f"**BIG FORTUNE:** {text}", width=60)
                display_text = '\n'.join(wrapped[:2])
                st.write(display_text)
            elif cat == "SMALL":
                wrapped = textwrap.wrap(f"**Small fortune:** {text}", width=60)
                display_text = '\n'.join(wrapped[:2])
                st.write(display_text)
            else:  # BAD
                wrapped = textwrap.wrap(f"**Bad luck:** {text}", width=60)
                display_text = '\n'.join(wrapped[:2])
                st.write(display_text)

        if last_iso:
            st.write(f"Last opened: {last_iso} UTC")
            last_f = state.get("last_fortune")
            if last_f:
                lcat = last_f.get("category")
                ltxt = last_f.get("text")
                if lcat == "BIG":
                    wrapped = textwrap.wrap(f"Previous: BIG FORTUNE — {ltxt}", width=60)
                    display_text = '\n'.join(wrapped[:2])
                    st.write(display_text)
                elif lcat == "SMALL":
                    wrapped = textwrap.wrap(f"Previous: Small fortune — {ltxt}", width=60)
                    display_text = '\n'.join(wrapped[:2])
                    st.write(display_text)
                else:
                    wrapped = textwrap.wrap(f"Previous: Bad luck — {ltxt}", width=60)
                    display_text = '\n'.join(wrapped[:2])
                    st.write(display_text)
            if not available and next_time:
                st.write(f"Next available: {next_time} UTC")
        else:
            st.write("You haven't opened a fortune yet.")

        with st.expander("Developer / testing tools"):
            if st.button("Reset cooldown (for testing)"):
                if os.path.exists(STATE_FILE):
                    try:
                        os.remove(STATE_FILE)
                    except Exception:
                        pass
                st.session_state.unavailable_warning = None
                st.session_state.current_fortune = None
                st.info("Cooldown reset. Refresh and open a new fortune.")


    elif Test == "Dice Roll":
        st.title("Dice Roll Fortune 🎲")

        luck_levels = {
            0: "Perfect intuition! Extremely lucky day ahead!",
            1: "Spot on! Very lucky!",
            2: "Only slightly off! A pretty Lucky day awaits!",
            3: "Really close!  Quite lucky!",
            4: "Not far off. Still quite lucky today.",
            5: "Your guess was a bit off. Average luck today",
            6: "Kind of off. A bit unlucky.",
            7: "You're off from the answer by some distance. Not the unluckiest, but still unlucky.",
            8: "Pretty bad guess. Bad luck might be incoming.",
            9: "Horrible guess. Prepare for challenges.",
            10: "You're completely off from the answer. Very bad luck awaits.",
            11: "Worst possible guess! The unluckiest day of your life might be ahead!"
        }

        state = load_state(STATE_FILE)
        last_dice_iso = state.get("last_dice_roll")
        available, next_time = can_roll(last_dice_iso, 10)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Pick a number (1-12), then roll the dice. Your luck is determined by how close your guess is to the roll. You can play once every 10 minutes.")
            guess = st.number_input("Pick your number (1-12):", min_value=1, max_value=12, step=1)
        with col2:
            if st.button("Roll the Dice 🎲"):
                if not available:
                    st.warning(f"You already rolled the dice. Next available: {next_time} UTC")
                elif not guess:
                    st.warning("Please pick a number first!")
                else:
                    roll = random.randint(1, 12)
                    diff = abs(guess - roll)
                    st.write(f"You picked {guess}, rolled a {roll}!")
                    st.write(f"Difference: {diff}")
                    st.write(luck_levels[diff])
                    state["last_dice_roll"] = datetime.utcnow().isoformat()
                    state["last_dice_guess"] = guess
                    state["last_dice_value"] = roll
                    save_state(STATE_FILE, state)

        # Display last roll
        if last_dice_iso:
            st.write(f"Last played: {last_dice_iso} UTC")
            last_guess = state.get("last_dice_guess")
            last_roll = state.get("last_dice_value")
            if last_guess is not None and last_roll is not None:
                last_diff = abs(last_guess - last_roll)
                st.write(f"Last guess: {last_guess}, roll: {last_roll} (difference: {last_diff}) - {luck_levels[last_diff]}")
            if not available and next_time:
                now = datetime.utcnow()
                remaining = next_time - now
                if remaining.total_seconds() > 0:
                    st.write(f"Time until next roll: {format_timedelta(remaining)}")
        else:
            st.write("You haven't played yet.")

        with st.expander("Developer / testing tools"):
            if st.button("Reset dice cooldown (for testing)"):
                state = load_state(STATE_FILE)
                if "last_dice_roll" in state:
                    del state["last_dice_roll"]
                if "last_dice_guess" in state:
                    del state["last_dice_guess"]
                if "last_dice_value" in state:
                    del state["last_dice_value"]
                save_state(STATE_FILE, state)
                st.info("Dice cooldown reset. Refresh and play again.")


    elif Test == "Coin Flip Streak":
        st.title("Coin Flip Streak Game 🪙")

        st.write("Guess heads or tails, then flip the coin. Build your winning streak!")

        choice = st.radio("Choose your guess:", ["Heads", "Tails"], horizontal=True)

        if st.button("Flip Coin 🪙"):
            result = random.choice(["Heads", "Tails"])
            if choice == result:
                if "streak" not in st.session_state:
                    st.session_state.streak = 0
                st.session_state.streak += 1
                st.success(f"🎉 Correct! It's {result}. Streak: {st.session_state.streak}")
            else:
                st.session_state.streak = 0
                st.error(f"❌ Wrong! It's {result}. Streak reset to 0.")

        # Display current streak
        current_streak = st.session_state.get('streak', 0)
        st.write(f"**Current Streak:** {current_streak}")

        # High score
        state = load_state(STATE_FILE)
        high_score = state.get("coin_high_score", 0)
        if current_streak > high_score:
            high_score = current_streak
            state["coin_high_score"] = high_score
            save_state(STATE_FILE, state)
        st.write(f"**High Score:** {high_score}")


    elif Test == "Custom Luck Test":
        st.title("AI Luck Test Builder 🤖")

        st.write("Describe the kind of luck test you'd like to create, and AI will help design it!")

        user_description = st.text_area("Describe your custom luck test idea with key words:", height=150, placeholder="E.g., A test involving colors and numbers, or something with cards...")

        if st.button("Design My Luck Test"):
            if user_description.strip():
                with st.spinner("Designing your custom luck test..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a professional luck test designer. Based on the user's description, create a well-structured luck-based test that interacts with the user's intuition. Provide clear, concise instructions and rules. Focus on practicality and clarity rather than expressive language. Explain how luck is determined in a straightforward manner."},
                                {"role": "user", "content": f"Design a luck test based on this idea: {user_description}"}
                            ]
                        )
                        ai_response = response.choices[0].message.content
                        st.success("Here's your custom luck test!")
                        st.write(ai_response)
                    except Exception as e:
                        st.error(f"Error designing test: {str(e)}")
            else:
                st.warning("Please describe your luck test idea first.")


if __name__ == "__main__":
    main()
