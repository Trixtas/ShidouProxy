from flask import Flask, request, Response, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('menu.html')

@app.route('/go')
def go():
    url = request.args.get('url')
    if url:
        # Internally call the proxy function instead of redirecting
        with app.test_request_context(f'/proxy?url={url}', method='GET', headers=request.headers):
            return proxy()
    else:
        return "Missing URL!", 400

@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing 'url' parameter", 400

    try:
        # Send the request to the target URL
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers.items() if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )

        # Filter out hop-by-hop headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        # Return the response to the client
        response = Response(resp.content, resp.status_code, headers)
        return response

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
