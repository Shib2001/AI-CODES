# Import the helper that reads values from a .env file.
from dotenv import load_dotenv
# Import Google's Generative AI library.
from google import genai

# Load GOOGLE_API_KEY from the .env file into the environment.
load_dotenv()

# Create the Google client; it reads GOOGLE_API_KEY automatically.
client = genai.Client()

# Send a prompt to Gemini and keep the response.
interaction = client.interactions.create(
    # Choose which Gemini model to use.
    model="gemini-3.7-flash",
    # Write your question or instruction as normal text here.
    input="Hello gemini how are you , my name is shiv",
)

# Print the text Gemini returned.
print(interaction.output_text)