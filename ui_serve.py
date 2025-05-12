import http.server
import socketserver
import socket
import os
import argparse
import urllib
from html import escape

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(404, "Directory not accessible")
            return None

        entries.sort(key=lambda a: a.lower())
        f = []
        displaypath = urllib.parse.unquote(self.path)

        f.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>📁 File Browser</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f8f9fa; }}
    h2 {{ color: #333; }}
    .container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }}
    .file-card {{
      background: white;
      padding: 12px;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      text-align: center;
      transition: 0.3s;
    }}
    .file-card:hover {{ transform: scale(1.02); }}
    a {{ text-decoration: none; color: #007bff; word-wrap: break-word; }}
    .icon {{ font-size: 40px; margin-bottom: 10px; }}
    footer {{ margin-top: 40px; font-size: 14px; color: #888; text-align: center; }}
  </style>
</head>
<body>
  <h2>📂 Index of {escape(displaypath)}</h2>
  <div class="container">""")

        if displaypath != '/':
            f.append(f"""<div class="file-card"><div class="icon">🔙</div><a href="../">.. (Parent Directory)</a></div>""")

        for name in entries:
            fullname = os.path.join(path, name)
            display_name = name + "/" if os.path.isdir(fullname) else name
            linkname = urllib.parse.quote(name)
            icon = "📁" if os.path.isdir(fullname) else "📄"

            f.append(f"""
            <div class="file-card">
                <div class="icon">{icon}</div>
                <a href="{linkname}">{escape(display_name)}</a>
            </div>
            """)

        f.append("""
      </div>
      <footer>🚀 Powered by Python http.server | Custom UI</footer>
    </body>
    </html>
        """)

        encoded = '\n'.join(f).encode('utf-8', 'surrogateescape')
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

def run_server(directory, port):
    os.chdir(directory)
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        local_ip = get_local_ip()
        print(f"\nServing '{directory}' at:")
        print(f"→ http://{local_ip}:{port}")
        print("Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve a directory over local network.")
    parser.add_argument("directory", help="Directory to share")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to use (default: 8000)")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("Error: Provided path is not a directory.")
    else:
        run_server(args.directory, args.port)
