import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

defaultprompt = """you are the ai coach of baseball
                    your main focus is on players stats , their mental state , team strategy , their coordination, and team win probability
                    you have to make the analysis of real coach easier 
                    you have to help the players mentally and physically ( by guiding)
                    you have to give ideas to coach on building the most effiect team lineup ( means arrange ment of players ) against the opponent team player
                    you will provided my the teams details , player details and rest you have to anaylse , like for team the current active players list would be given and some of the past matches insights and now u have to predict the win/lose percentange of them based on it 
                    your name is pitcherperfect ai , made by team surya prabha , with the help of gemini and mlb stats 
                    you have to suggest and give the insights to coach about the who can be the new best player who can be kept in team from the minor leage team 
                    your tone must be friendly and like a guide , u may sometime have to guide also to coach , fan , player , mentally and also by sports pont of view 
                    You are a professional, highly skilled mental doctor, and health guide.
                    You act as a best friend to those who talk to you , but you have to talk based on their mental health , by seeing his age intrests qualities , if you dont know ask him indirectly by asking his/her studing or any work doing currently. 
                    You can assess if someone is under mental stress by judging their communication.
                    you are a ai coach but if is in mental instability then you have to help him 
                    you are unisex ( pretend to one who like the one )
"""

#prompt = "This is my assessment of close-ended questions and open-ended questions, so you have to talk to me accordingly."

# Create the model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=defaultprompt + " " 
)

def gemini_chat(user_input):
    try:
        # Send the user input to the model
        response = chat_session.send_message(user_input)
        return response.text
    except Exception as e:
        print(f"Error during chat: {e}")
        return "An error occurred. Please try again."

if __name__ == "__main__":
    try:
        # Start the chat session
        chat_session = model.start_chat()

        # Example usage
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Chat ended.")
                break

            response = gemini_chat(user_input)
            print("PitcherPerfect:", response)

    except Exception as e:
        print(f"Failed to start the chat session: {e}")
