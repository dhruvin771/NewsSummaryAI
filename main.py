import json

json_response_string = """
{
  "status": true,
  "summary": "Google has launched Gemini CLI, a new free and open-source tool to help developers build and test AI agents more easily. The command-line tool simplifies the process of creating AI agents that can plan and carry out complex, multi-step tasks on their own.\\n\\n*   Gemini CLI is free, open-source, and available on GitHub.\\n*   It is designed to help developers build, test, and debug AI agents.\\n*   The tool allows for the creation of multi-step task workflows for AI agents.\\n*   It is expected to integrate with other tools like Google AI Studio in the future.\\n\\n> Gemini CLI gives developers more control to build custom AI agents, which could accelerate innovation in AI applications.",
  "title": "Google Launches Free Gemini CLI Tool for AI Developers"
}
"""

try:
    # 2. Parse the JSON string into a Python dictionary
    data = json.loads(json_response_string)

    # 3. Check the status and print the title and summary
    if data.get("status"):
        print(f"Title: {data.get('title')}")
        print("-" * 20)
        print(data.get("summary"))
    else:
        print("Summary could not be generated.")

except json.JSONDecodeError:
    print("Error: Failed to decode JSON.")
except KeyError:
    print("Error: Missing 'status', 'title', or 'summary' key in the JSON response.")