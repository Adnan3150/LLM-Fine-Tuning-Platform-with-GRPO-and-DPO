import threading
from flask import Flask, request, render_template_string, redirect, url_for
import uuid
from app.state import session_store, prompt_queue, state_lock
def create_app():
    app = Flask(__name__)
      
    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            prompt = request.form.get("prompt")
            session_id = str(uuid.uuid4())

            with state_lock:
                prompt_queue.append({"session_id": session_id, "prompt": prompt})
                session_store[session_id] = {
                    "prompt": prompt,
                    "num_of_epochs": 0
                }

            return redirect(url_for('rate', session_id=session_id))

        return """
        <html>
        <head>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body, html {
                    height: 100%;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                }
                .footer-form {
                    margin-top: auto;
                    padding: 20px;
                    background: #f8f9fa;
                    border-top: 1px solid #dee2e6;
                }
            </style>
        </head>
        <body>
            <div class="container-fluid footer-form">
                <form method='POST'>
                    <div class="mb-3">
                        <textarea class="form-control" name="prompt" rows="4" placeholder="Enter your prompt..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit Prompt</button>
                </form>
            </div>
        </body>
        </html>
        """

    @app.route("/rate/<session_id>", methods=["GET", "POST"])
    def rate(session_id):
        session = session_store.get(session_id)

        if session is None:
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Generating Completions</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <meta http-equiv="refresh" content="2">
                <style>
                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background-color: #f8f9fa;
                    }

                    .loader-container {
                        text-align: center;
                    }

                    .loader {
                        border: 4px solid #f3f3f3; /* Light grey border */
                        border-top: 4px solid #3498db; /* Blue border for the spinning part */
                        border-radius: 50%;
                        width: 50px;
                        height: 50px;
                        animation: spin 2s linear infinite;
                        margin-bottom: 15px;
                    }

                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="loader-container">
                    <div class="loader"></div>
                    <p class="mt-3">Model is generating completions... Please wait.</p>
                </div>
            </body>
            </html>"""

        if session.get("num_of_epochs") == 2:
            return "<div class='container mt-5'><p class='alert alert-success'>Final submission done. Thanks!</p></div>"

        if not session.get("completions") and session.get("num_of_epochs") < 2:
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Generating Completions</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <meta http-equiv="refresh" content="2">
                <style>
                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background-color: #f8f9fa;
                    }

                    .loader-container {
                        text-align: center;
                    }

                    .loader {
                        border: 4px solid #f3f3f3; /* Light grey border */
                        border-top: 4px solid #3498db; /* Blue border for the spinning part */
                        border-radius: 50%;
                        width: 50px;
                        height: 50px;
                        animation: spin 2s linear infinite;
                        margin-bottom: 15px;
                    }

                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="loader-container">
                    <div class="loader"></div>
                    <p class="mt-3">Model is generating completions... Please wait.</p>
                </div>
            </body>
            </html>
            """

        if request.method == "POST":
            session["feedbacks"] = []
            for i in range(len(session["completions"])):
                session["ratings"][i] = float(request.form.get(f"rating_{i}"))
                feedback = request.form.get(f"feedback_{i}", "")
                session["feedbacks"].append(feedback)

            session["num_of_epochs"] += 1
            session["event"].set()
            return redirect(url_for('rate', session_id=session_id))

        if session["num_of_epochs"] < 2 and None in session["ratings"]:
            html = """
            <html>
            <head>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <h2 class="mb-4">Prompt:</h2>
                    <p class="alert alert-secondary">{prompt}</p>
                    <form method="POST">
            """.format(prompt=session["prompt"])

            for i, completion in enumerate(session["completions"]):
                html += f"""
                    <div class="card mb-4">
                        <div class="card-body">
                            <h5 class="card-title">Completion {i+1}</h5>
                            <p class="card-text" style="white-space: pre-wrap;">{completion}</p>
                            <div class="mb-3">
                                <label for="rating_{i}" class="form-label">Rate (0-1):</label>
                                <input type="number" class="form-control" name="rating_{i}" min="0" max="1" step="0.05" required>
                            </div>
                            <div class="mb-3">
                                <label for="feedback_{i}" class="form-label">Feedback:</label>
                                <textarea class="form-control" name="feedback_{i}" rows="3" placeholder="Enter feedback..."></textarea>
                            </div>
                        </div>
                    </div>
                """


            html += """
                    <button type="submit" class="btn btn-success">Submit Ratings & Feedback</button>
                    </form>
                </div>
            </body>
            </html>
            """
            return html

        return "<div class='container mt-5'><p class='alert alert-info'>Already rated. Thanks!</p></div>"

    return app
