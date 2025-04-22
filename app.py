from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        resp = requests.get(target_url)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=5000)
