from flask import Flask, request, Response, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('menu.html')

@app.route('/go')
def go():
    url = request.args.get('url')
    if not url:
        return "Missing URL!", 400
    # Directly forward to proxy
    return proxy(url)

@app.route('/proxy', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def proxy(target_url=None):
    if not target_url:
        target_url = request.args.get("url")
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        # Forward request
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key.lower() != "host"},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )

        # Filter hop-by-hop headers
        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
