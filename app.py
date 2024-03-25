import os
import threading

from flask import Flask, render_template, request, Response, redirect

from database import init_db_if_not_exists, find_data_by_uuid, increase_qr_clicked_count
from qr_generator import QRGenerator

app = Flask(__name__)

# get the domain and database name for the qr code, which is saved as ENV variable
DOMAIN: str | None = os.getenv("DOMAIN")
DATABASE_NAME: str | None = os.getenv("DATABASE_NAME")

# TODO: delete - testing purposes
#DOMAIN = "http://localhost:5000/"
#DATABASE_NAME = "qr.db"

DATABASE_NAME = "/database/"+DATABASE_NAME

init_db = init_db_if_not_exists(DATABASE_NAME)

qr_gen = QRGenerator(DOMAIN, DATABASE_NAME)


@app.route('/')
def index():
    return render_template("./index.html")


@app.route('/qr', methods=["POST"])
def generate_qr():
    data = request.form["url"]
    back_color = request.form["background"]

    # we create a mapping, an uuid will be saved to the database
    # with the corresponding data which we got from the request
    # the qr_data, will then be turned into the qr code
    qr_data = qr_gen.generate_qr_code_data(data)

    qr = qr_gen.generate_qr_code(qr_data, back_color=back_color)

    encoded_img_data = qr_gen.encode_base64_in_memory(qr)
    utf8_img_data = encoded_img_data.decode("utf-8")

    return render_template("./show_qr.html", url_name=data, img_data=utf8_img_data)


@app.route('/download', methods=["POST"])
def download():
    # Get the img_data from the form data
    img_data = request.form.get('img_data')

    img_data = img_data.encode('utf-8')
    img_data = qr_gen.decode_base64(img_data)

    response = Response(img_data, mimetype="image/png")
    response.headers["Content-Disposition"] = "attachment; filename=qr.png"

    # Return the response for download
    return response


@app.route('/<uuid>')
def redirect_by_uuid(uuid):
    # get the url data from the database
    url_data = find_data_by_uuid(uuid, DATABASE_NAME)

    # if the url data is not None, we redirect to the url
    if url_data is None:
        # TODO: change to 404 page
        return "404"

    # Start a new thread to update the count without waiting for it to complete
    threading.Thread(target=increase_qr_clicked_count, args=(uuid, DATABASE_NAME)).start()

    return redirect(url_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # TODO: make this code save for production
    # TODO: how much traffic can the server handle?
