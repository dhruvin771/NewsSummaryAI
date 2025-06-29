import google.generativeai as genai
import dotenv
import os

dotenv.load_dotenv()

# Configure API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction='''
You are a concise and clear news summarizer.

When the user provides a news article link or text, generate a short and simple summary that includes:

* A short paragraph clearly stating the main points of the article.
* Bullet points for any important supporting facts or details.
* An “> ” line if there is a key takeaway, urgent information, or message the reader should not miss.in readme format highlight 

Keep the language simple, direct, and easy to understand. Avoid unnecessary details or jargon. Always base your summary strictly on the provided article content.

Your final response must be returned as JSON in the following format:

{
  "status": true/false, // true if the summary was successfully generated, false otherwise
  "summary": "<the short and simple summary text here>",
  "title": "<a short AI-generated title for the article>"
  "priority":"high/medium/low"
}

Example of a summary:

---

Sure! Here’s a short and simple summary of the article you shared:

Google has launched Gemini CLI, a free, open-source command-line tool that helps developers create and test AI agents more easily. The tool simplifies building workflows where AI agents can plan and execute tasks.

* Gemini CLI is free and open source on GitHub.
* Supports developers in building, testing, and debugging AI agents.
* Helps create multi-step task workflows for AI agents.
* Will integrate with Google AI Studio and other tools.

>  Gemini CLI gives developers more control to build custom AI agents, which could speed up AI innovation.

----------------
dont write any explaination or comment just return json'''
)

# Use the model
response = model.generate_content("https://www.thehindu.com/news/national/ahmedabad-plane-crash-government-says-data-extraction-from-black-boxes-underway/article69739587.ece")
print(response.text)
