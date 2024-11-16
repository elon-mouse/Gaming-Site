# simple_web_server.py
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import os

# Set the port and directory
PORT = 80  # Use port 80
DIRECTORY = "/home/arman/gfiles/games"  # Path to your game files

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def list_directory(self, path):
        """Override to generate a directory listing with links to each file."""
        try:
            # List all files and directories
            files = os.listdir(path)
            files.sort()

            # Generate HTML for the file list with a nicer layout
            output = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Gaming Files</title>
                <link rel="stylesheet" href="style.css">
            </head>
            <body>
                <header>
                    <h1>Welcome to the Gaming File Server!</h1>
                </header>
                <main>
                    <h2>Available Game Files</h2>
                    <ul>
            """

            # Create a link for each file
            for file in files:
                display_name = file
                link_name = file
                output += f'<li><a href="{link_name}">{display_name}</a></li>'

            output += """
                    </ul>
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
            return None
        except OSError:
            self.send_error(404, "File not found")

# Start the server
with TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Serving at port {PORT} from directory: {DIRECTORY}")
    httpd.serve_forever()

