import http.server
import socketserver
import socket
import os
import argparse

def get_local_ip():
    """Get the local IP address of the host (not 127.0.0.1)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_server(directory, port):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
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
