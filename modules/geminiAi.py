import google.generativeai as genai
import os
from dotenv import load_dotenv
from prompt import prompt
# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))
defaultprompt = prompt()
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
