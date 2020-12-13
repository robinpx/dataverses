from flask import Flask, render_template
import json
import hewitt_images

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/image', methods=['GET'])
def image():
    data = hewitt_images.get_image()
    response = app.response_class(
        response=json.dumps(data),
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(debug = True)
