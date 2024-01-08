import base64
import io

from flask import Flask, render_template, request, Response

from qr_code import generate_qr_code, encode_base64_in_memory

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template("./index.html")


@app.route('/qr', methods=["POST"])
def generate_qr():
    data = request.form["url"]
    back_color = request.form["background"]

    qr = generate_qr_code(data, back_color=back_color)

    encoded_img_data = encode_base64_in_memory(qr)
    utf8_img_data = encoded_img_data.decode("utf-8")

    return render_template("./show_qr.html", url_name=data, img_data=utf8_img_data)


@app.route('/download', methods=["POST"])
def download():
    # Get the img_data from the form data
    img_data = request.form.get('img_data')

    img_data = img_data.encode('utf-8')
    img_data = base64.b64decode(img_data)

    response = Response(img_data, mimetype="image/png")
    response.headers["Content-Disposition"] = "attachment; filename=qr.png"

    # Return the response for download
    return response


if __name__ == '__main__':
    app.run()
