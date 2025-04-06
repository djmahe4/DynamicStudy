from google import genai
from google.genai import types
import os
import streamlit as st
import random
import sys
from dotenv import load_dotenv, find_dotenv
from pylatexenc.latex2text import LatexNodes2Text
import time
#import msvcrt

def latex_to_unicode(latex_str):
    return LatexNodes2Text().latex_to_text(latex_str)
# Load existing .env file or create one if it doesn't exist
import threading
class pqrs_t_study_session:
    def __init__(self, wm, count):
        self.material = st.text_input("Enter the material: ")
        self.work_minutes = wm
        self.count = count
        #self.model = genai.get_model("models/chat-bison-001")

    def generate(self,client, full_prompt="+page replacement techniques"):

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"""{full_prompt}"""),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
        )
        a = "".join(item.text for item in
                    client.models.generate_content_stream(model=model, contents=contents,
                                                          config=generate_content_config))
        return a
    def preview_material(self, material):  # Receive chat as an argument
        prompt = f"Spark Curiosity! Imagine you're explaining this to a friend who's new to it. What's the most important things you'd tell them about {material}?"
        response = self.generate(st.session_state.client,prompt)
        return latex_to_unicode(response)

    def ask_questions(self, material):
        prompt_options = [
            f"\n**Curiosity Prompt!** What specific questions I need to have about this topic {material}? Provide answers"
        ]
        prompt = random.choice(prompt_options)
        response = self.generate(st.session_state.client, prompt)
        return latex_to_unicode(response)

    def read_and_study(self, material):
        prompt = f"**Teach me in detail about {material}(Please Explain with diagrams if possible)."
        response = self.generate(st.session_state.client, prompt)
        return latex_to_unicode(response)

    def summarize_key_points(self,material):
        prompt = f"**Reinforce Learning!** \nIf you could explain this topic in just 3-5 sentences to someone else, what would you say?\n"
        summary = st.text_input(prompt)
        st.write()
        # Here you can add logic to analyze the summary and provide feedback
        if summary:
            feedback = f"This is my summary: {summary} ;please give me a score out of 10 and higlight the points i missed out and what should i improve regarding the topic {material}?."
            response = self.generate(st.session_state.client, prompt)
            return latex_to_unicode(response)
        else:
            return "summary not given in the python window"

    def test_understanding(self,material):
        prompt_options = [
            f"\n**Self-Quiz!** Create your own multiple-choice, true/false, or fill-in-the-blank questions based on {material}.",
            f"\n**Challenge a Friend!** Explain a concept to a friend and see if they can understand the {material}.",
            f"\n**Gamification!** Create a quiz python app or learning game (e.g., Kahoot!, Quizlet Live) to test yourself in a fun way about the topic {material}."
        ]
        prompt = random.choice(prompt_options)
        response = self.generate(st.session_state.client, prompt)
        return latex_to_unicode(response)

    def run(self):
        # Assuming model is defined elsewhere
        #chat = self.model.start_chat()  # Create chat object here
        st.write('\nPREVIEW:')
        st.write(self.preview_material(self.material))
        self.count(60*2)
        st.write("\nQUESTIONS:")
        #time.sleep(120)  # Wait for 25 seconds
        st.write(self.ask_questions(self.material))
        self.count(60 * 4)
        st.write("\nSTUDY:")
        #time.sleep(240)  # Wait for 25 seconds
        st.write(self.read_and_study(self.material))
        self.count(60 * 8)
        #time.sleep(480)  # Wait for 25 seconds
        st.write("\nSUMMARY:")
        st.write(self.summarize_key_points(self.material))
        self.count(60 * 8)
        st.write("\nTEST:")
        #time.sleep(480)  # Wait for 25 seconds
        st.write(self.test_understanding(self.material))
        self.count(60 * 3)

        # Use threading for timed execution
        #work_thread = threading.Thread(target=self._timed_work, args=(self.work_minutes,))
        #work_thread.start()
        #work_thread.join()  # Wait for work to finish
        # Pass chat as argument (if needed)

        # ... (similar logic for other stages using _timed_work and potentially passing chat)

    def _timed_work(self, duration_minutes):
        duration_seconds = duration_minutes * 60
        end_time = time.time() + duration_seconds
        while time.time() < end_time:
            st.write(f"time is up!")
            # for _ in range(5):  # Beep for 5 seconds
            #     beepy.beep(sound='ping')  # 'ping' is one of the provided sounds
            #     time.sleep(1)
            # Perform non-blocking tasks here (e.g., user interaction)
            pass  # Placeholder for non-blocking activities

class PomodoroTimer:
    def __init__(self, work_minutes=25, short_break_minutes=5, long_break_minutes=10, cycles=4):
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.cycles = cycles

    def run(self):
        for cycle in range(self.cycles):
            self._work()
            self._short_break()
            if cycle == self.cycles - 1:
                self._long_break()
            else:
                self._short_break()

    def input_available(self,key):
        """Placeholder function for checking user input (replace with actual implementation)."""
        # This example checks for a key press using a short timeout
        #import msvcrt  # For Windows
        if st.button("Skip",key=key):  # Consume the keypress
            return True
        return False
    def _countdown(self, seconds):
        while seconds > 0:
            sys.stdout.write("\r{} seconds remaining".format(seconds))
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
            # Play beeps for the last 5 seconds
            # if seconds <= 5 and seconds > 1:
            #     beepy.beep(sound='ping')  # Adjust sound as needed
            # if seconds == 1:
            #     beepy.beep(sound='ready')
            if self.input_available(key=seconds):  # Replace with your function to check for user input
                st.write("Countdown stopped by user!")
                break

    def _work(self):
        s = pqrs_t_study_session(self.work_minutes, self._countdown)  # Create an instance of pqrs_t_study_session
        #self._countdown(self.work_minutes * 60)
        #x = self
        if s.material:
            s.run()  # Pass self (PomodoroTimer object) to pqrs_t_study_session.run

    def _short_break(self):
        st.write("Taking a short break for {} minutes.".format(self.short_break_minutes))
        self._countdown(self.short_break_minutes * 60)

    def _long_break(self):
        st.write("Taking a long break for {} minutes.".format(self.long_break_minutes))
        self._countdown(self.long_break_minutes * 60)

    #cont = st.text_input("CYCLE over DO you want to CONTINUE (Y/N)", default='n')
    #if cont.lower() != 'y':
        #return
if __name__ == "__main__":
    # Create a Pomodoro timer object and run it
    while True:
        timer = PomodoroTimer()
        timer.run()
        cont=st.text_input("CYCLE over DO you want to CONTINUE (Y/N)",default='n')
        if cont.lower() != 'y':
            break