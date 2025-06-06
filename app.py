from flask import Flask, render_template, request, redirect
import os
from image_dna_logic import process_and_store, compare_image
from image_dna_logic import init_db
init_db()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image" not in request.files:
            return "No file part"

        file = request.files["image"]

        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # compare first, then optionally store
            is_match = compare_image(filepath)
            process_and_store(filepath)  # only store new image regardless for now. probably will consider saving a old image for it

            if is_match:
                return f"Image {file.filename} is similar to an existing one."
            else:
                return f"Image {file.filename} is unique and has been stored."

    return render_template("imageDNA.html")

if __name__ == "__main__":
    app.run(debug=True)
