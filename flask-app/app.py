from flask import Flask, request, Response, render_template
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('menu.html')

@app.route('/go')
def go():
    url = request.args.get('url')
    if url:
        return f'<meta http-equiv="refresh" content="0; url=/proxy?url={quote(url)}">'
    else:
        return "Missing URL!", 400

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        resp = requests.get(target_url, headers={key: value for (key, value) in request.headers if key.lower() != 'host'}, stream=True)

        content_type = resp.headers.get("Content-Type", "")
        content = resp.content

        # If HTML, rewrite links
        if "text/html" in content_type:
            soup = BeautifulSoup(resp.text, "html.parser")

            # Rewrite all href/src/action attributes
            for tag in soup.find_all(["a", "link", "script", "img", "form"]):
                attr = "href" if tag.name in ["a", "link"] else "src" if tag.name in ["script", "img"] else "action"
                if tag.has_attr(attr):
                    original = tag[attr]
                    new_url = urljoin(target_url, original)
                    tag[attr] = f"/proxy?url={quote(new_url)}"

            content = str(soup).encode("utf-8")
            content_type = "text/html"

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]

        return Response(content, resp.status_code, headers)

    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
