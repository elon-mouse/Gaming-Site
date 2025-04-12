from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import cookies
from urllib.parse import parse_qs
import html
import os

PORT = 80
DIRECTORY = "/home/arman/gfiles/games"
FEEDBACK_FILE = "/home/arman/gfiles/feedback.txt"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def is_authenticated(self):
        if "Cookie" in self.headers:
            c = cookies.SimpleCookie(self.headers["Cookie"])
            if "authenticated" in c and c["authenticated"].value == "yes":
                return True
        return False

    def list_directory(self, path):
        try:
            files = os.listdir(path)
            files.sort()

            output = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Gaming Files</title>
                <style>
                    body {
                        background-color: #121212;
                        color: #e0e0e0;
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
                        background-color: #1e1e1e;
                        border-radius: 8px;
                        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
                    }
                    header h1 {
                        font-size: 2.5em;
                        color: #4fc3f7;
                    }
                    main h2 {
                        font-size: 1.8em;
                        color: #f5f5f5;
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
                        color: #f5f5f5;
                        text-decoration: none;
                        font-size: 1.2em;
                        transition: color 0.3s ease;
                    }
                    ul li a:hover {
                        color: #4fc3f7;
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
                    #searchInput {
                        width: 100%;
                        max-width: 400px;
                        padding: 10px;
                        margin: 10px auto 20px auto;
                        font-size: 1em;
                        border-radius: 4px;
                        border: 1px solid #4fc3f7;
                        background-color: #1e1e1e;
                        color: #e0e0e0;
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
                    <input type="text" id="searchInput" placeholder="Search files..." onkeyup="filterFiles()">
                    <ul id="fileList">
            """

            for file in files:
                display_name = html.escape(file)
                link_name = html.escape(file)
                output += f'<li><a href="{link_name}">{display_name}</a></li>'

            output += """
                    </ul>
                    <h2>Feedback</h2>
                    <form action="/submit_feedback" method="POST">
                        <textarea name="feedback" placeholder="Your feedback here..." required></textarea>
                        <button type="submit">Submit Feedback</button>
                    </form>
                </main>
                <footer>
                    <p>Powered by Arman Khodayarinezhad | Your Gaming Hub</p>
                </footer>
                <script>
                    function filterFiles() {
                        const input = document.getElementById("searchInput");
                        const filter = input.value.toLowerCase();
                        const ul = document.getElementById("fileList");
                        const items = ul.getElementsByTagName("li");

                        for (let i = 0; i < items.length; i++) {
                            const a = items[i].getElementsByTagName("a")[0];
                            const textValue = a.textContent || a.innerText;
                            if (textValue.toLowerCase().indexOf(filter) > -1) {
                                items[i].style.display = "";
                            } else {
                                items[i].style.display = "none";
                            }
                        }
                    }
                </script>
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
        if self.path == "/admin_login":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.render_login_form().encode("utf-8"))

        elif self.path == "/admin_feedback":
            if self.is_authenticated():
                feedback = self.read_feedback_logs()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(feedback.encode("utf-8"))
            else:
                self.send_response(403)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Access denied. Please login at <a href='/admin_login'>/admin_login</a>.")

        elif self.path == "/logout":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Set-Cookie", "authenticated=; Max-Age=0; Path=/")
            self.end_headers()
            self.wfile.write(b"Logged out successfully. <a href='/'>Go back</a>.")

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/submit_feedback":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            feedback = parse_qs(post_data.decode('utf-8')).get('feedback', [""])[0]

            if feedback:
                feedback = html.escape(feedback)
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

        elif self.path == "/admin_login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = parse_qs(post_data.decode('utf-8'))

            username = post_data.get('username', [None])[0]
            password = post_data.get('password', [None])[0]

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                c = cookies.SimpleCookie()
                c["authenticated"] = "yes"
                c["authenticated"]["path"] = "/"

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Set-Cookie", c.output(header='', sep=''))
                self.end_headers()
                self.wfile.write(b"Login successful! Go to <a href='/admin_feedback'>/admin_feedback</a> to view feedback.")
            else:
                self.send_response(401)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Login failed! Incorrect username or password.")

    def render_login_form(self):
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Login</title>
        </head>
        <body>
            <h1>Admin Login</h1>
            <form action="/admin_login" method="POST">
                <input type="text" name="username" placeholder="Username" required><br><br>
                <input type="password" name="password" placeholder="Password" required><br><br>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """

    def read_feedback_logs(self):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                feedback = f.readlines()
                return """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Feedback Logs</title>
                </head>
                <body>
                    <h1>Feedback Logs</h1>
                    <ul>
                """ + ''.join([f"<li>{html.escape(line.strip())}</li>" for line in feedback]) + """
                    </ul>
                    <a href='/logout'>Logout</a>
                </body>
                </html>
                """
        except FileNotFoundError:
            return "<h1>No feedback yet!</h1>"

# Start the server
with HTTPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT} from directory: {DIRECTORY}")
    httpd.serve_forever()
