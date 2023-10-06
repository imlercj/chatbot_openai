from flask import Flask, request, render_template, session, redirect
import uvicorn
from chatbot import Chatbot
app = Flask(__name__)

# Set secret key for session
app.secret_key = "secret"

#initiate chatbot
chatbot = Chatbot()

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        print('request', request.args)
        # get the user input
        msg = request.form["input_text"]
        # get the bot response
        response_text = chatbot.chatbot_response(msg)

    else:
        response_text = ""
        msg = ""
    print('msg: ', msg)
    return render_template("index.html", input_text=msg, response_text=response_text, history=chatbot.output_history)

@app.route('/reset', methods=['POST'])
def reset():
    # Reset the chat history
    chatbot.reset_history()
    # Redirect to the chat page
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
    msg = "Was Niche right?"
    print(chatbot.chatbot_response(msg, chatbot.output_history))