from flask import Flask, request, Response, render_template, redirect
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('menu.html')

@app.route('/go')
def go():
    url = request.args.get('url')
    if url:
        return redirect(f'/proxy?url={url}')
    else:
        return "Missing URL!", 400

@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers.items() if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=5000)
