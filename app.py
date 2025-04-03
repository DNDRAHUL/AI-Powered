from flask import Flask, request, jsonify, session
from phi.agent import Agent
from phi.model.google import Gemini
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for session handling

# Set Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyA2EMWmxFC24ww1chHcQylw6BkzzLrpA6k"

# Define the Gemini agent
agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    show_tool_calls=True,
    markdown=True,
)



# Endpoint to start the conversation
@app.route('/start-conversation', methods=['POST'])
def start_conversation():
    try:
        input_data = request.get_json()
        job_title = input_data.get("job_title", "Developer")  # Default
        no_of_experience = input_data.get("no_of_experience", 0)  # Default

        # Save initial context in session
        session["context"] = {
            "job_title": job_title,
            "no_of_experience": no_of_experience,
            "conversation_history": []  # To track the conversation
        }

        # Generate the initial response
        instructions = [
            f"Create a comprehensive learning roadmap for a {no_of_experience}-year experienced {job_title}.",
            "Provide the roadmap step by step, and dynamically include relevant topics based on the job title and experience level.",
            "Additionally, include links to resources such as video tutorials, official documentation, open-source projects, and articles for each step in the roadmap."
        ]

        # Generate the response
        response = agent.run(" ".join(instructions))

        # Update session with the agent's response
        session["context"]["conversation_history"].append({
            "agent": response.content
        })

        # Return the initial response
        return jsonify({
            "status": "success",
            "message": response.content.split("\n")
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Endpoint to continue the conversation
@app.route('/continue-conversation', methods=['POST'])
def continue_conversation():
    try:
        input_data = request.get_json()
        user_input = input_data.get("user_input", "")

        # Retrieve context from session
        context = session.get("context", {})
        if not context:
            return jsonify({
                "status": "error",
                "message": "Conversation not started. Use /start-conversation first."
            }), 400

        # Update conversation history with user's input
        context["conversation_history"].append({
            "user": user_input
        })

        # Generate the next instructions based on user input
        instructions = [
            f"User input: '{user_input}'.",
            "Provide the next step in the roadmap along with relevant resource material such as video tutorials, documentation, articles, and open-source projects."
        ]

        # Generate the agent's response
        response = agent.run(" ".join(instructions))

        # Update session with the agent's response
        context["conversation_history"].append({
            "agent": response.content
        })
        session["context"] = context

        # Return the agent's response
        return jsonify({
            "status": "success",
            "message": response.content.split("\n")
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
