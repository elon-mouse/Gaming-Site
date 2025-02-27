from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from urllib.parse import parse_qs

PORT = 80
DIRECTORY = "/home/arman/gfiles/games"
FEEDBACK_FILE = "/home/arman/gfiles/feedback.txt"

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def list_directory(self, path):
        try:
            files = os.listdir(path)
            files.sort()

            # Generate HTML with a dark theme
            output = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Gaming Files</title>
                <style>
                    body {
                        background-color: #121212; /* Dark background */
                        color: #e0e0e0; /* Light text color */
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        min-height: 100vh;
                    }
                    header, main, footer {
                        width: 80%;
                        max-width: 800px;
                        text-align: center;
                        margin: 20px 0;
                        padding: 20px;
                        background-color: #1e1e1e; /* Slightly lighter for contrast */
                        border-radius: 8px;
                        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
                    }
                    header h1 {
                        font-size: 2.5em;
                        color: #4fc3f7; /* Accent color */
                    }
                    main h2 {
                        font-size: 1.8em;
                        color: #f5f5f5; /* Accent color */
                    }
                    ul {
                        list-style-type: none;
                        padding: 0;
                        margin: 15px 0;
                    }
                    ul li {
                        margin: 10px 0;
                    }
                    ul li a {
                        color: #f5f5f5; /* Link color */
                        text-decoration: none;
                        font-size: 1.2em;
                        transition: color 0.3s ease;
                    }
                    ul li a:hover {
                        color: #4fc3f7; /* Light hover color */
                    }
                    form {
                        margin-top: 20px;
                    }
                    textarea {
                        width: 100%;
                        height: 100px;
                        margin-bottom: 10px;
                        padding: 10px;
                        background-color: #1e1e1e;
                        color: #e0e0e0;
                        border: 1px solid #4fc3f7;
                        border-radius: 4px;
                    }
                    button {
                        padding: 10px 20px;
                        background-color: #4fc3f7;
                        color: #121212;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }
                    button:hover {
                        background-color: #357abd;
                    }
                    footer p {
                        font-size: 0.9em;
                        color: #888888;
                    }
                </style>
            </head>
            <body>
                <header>
                    <h1>Welcome to the Gaming File Server!</h1>
                </header>
                <main>
                    <h2>Available Game Files</h2>
                    <ul>
            """
            for file in files:
                display_name = file
                link_name = file
                output += f'<li><a href="{link_name}">{display_name}</a></li>'

            output += """
                    </ul>
                    <h2>Feedback</h2>
                    <form action="/submit_feedback" method="POST">
                        <textarea name="feedback" placeholder="Your feedback here..." required></textarea>
                        <button type="submit">Submit Feedback</button>
                    </form>
                    <h2>Or visit our external proxy</h2>
                    <a href="/redirect">Click here to go to the proxy website</a>
                </main>
                <footer>
                    <p>Powered by Arman Khodayarinezhad | Your Gaming Hub</p>
                </footer>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(output.encode("utf-8"))
        except OSError:
            self.send_error(404, "File not found")

    def do_GET(self):
        """Serve CSS file, redirect or default behavior."""
        if self.path == "/style.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open("/home/arman/gfiles/style.css", "r") as css_file:
                self.wfile.write(css_file.read().encode("utf-8"))
        elif self.path == "/redirect":
            # Redirect to the external website
            self.send_response(301)
            self.send_header("Location", "http://proxy.byteoftech.net")
            self.end_headers()
        else:
            super().do_GET()

    def do_POST(self):
        """Handle feedback submissions."""
        if self.path == "/submit_feedback":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            feedback = parse_qs(post_data.decode('utf-8')).get('feedback', [""])[0]

            if feedback:
                with open(FEEDBACK_FILE, "a") as f:
                    f.write(feedback + "\n")
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Thank you for your feedback!")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Feedback submission failed.")

# Start the server
with HTTPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT} from directory: {DIRECTORY}")
    httpd.serve_forever()

