import requests
from pprint import pprint
from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from twilio.twiml.messaging_response import Message, MessagingResponse

from constants import PARENT_DIRECTORY, RESULT_IMAGE_FOLDER, HOST_URL

# https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply-python
from helper import get_bytes_image_from_url
from image_classifier import get_image_classification
from job_submit import get_wrnch_data
from resize_image import get_resize
from rotate_image import get_rotation
from app import app

CORS(app)
FILE_NAME = "info_images/volleyball.jpg"


def resolve_url(url_link):
    get_response = requests.get(url=url_link)
    final_url = get_response.url
    return final_url


@app.route("/", methods=["GET"])
def hello():
    return "Hello ! Server is running good!!"


@app.route("/result_images/<filename>", methods=["GET"])
def sent_image(filename):
    return send_file(f"{RESULT_IMAGE_FOLDER}/{filename}", as_attachment=True)


@app.route("/show_image/<filename>", methods=["GET"])
def show_image(filename):
    return render_template("index.html", user_image=f"/result_images/{filename}")


@app.route("/message", methods=["GET", "POST"])
def message():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    received_data = request.values
    pprint(f"received_data={received_data}")
    received_body_msg = request.values.get("Body", None)
    print(f"body={received_body_msg}")
    media_url = received_data.get("MediaUrl0")
    print(f"media_url={media_url}")
    # Start our TwiML response
    response = MessagingResponse()
    message_twilio = Message()
    if media_url:
        resolved_url = resolve_url(media_url)
        print(f"resolved_url={resolved_url}")
        if received_body_msg.startswith("Image_"):
            store_file_name = f'{received_body_msg.replace("Image_", "")}.jpg'
            r = requests.get(resolved_url, stream=True)
            image_classes = get_image_classification(image_url=resolved_url)
            with open(f"{PARENT_DIRECTORY}/info_images/{store_file_name}", "wb") as f:
                f.write(r.content)
            response_text = (
                f"Uploaded File: {store_file_name} has classes={image_classes}"
            )
            message_twilio.body(response_text)
            response.append(message_twilio)
            return str(response)

        elif received_body_msg.startswith("Resize_"):
            file_name = f'{received_body_msg.replace("Resize_", "")}.jpg'

        else:
            file_name = "volleyball.jpg"
        operation_file_path = f"{PARENT_DIRECTORY}/info_images/{file_name}"
        binary_image = get_bytes_image_from_url(url=resolved_url)
        (
            wrist_dist,
            shoulder_dist,
            left_wrist_displ,
            right_wrist_displ,
            rotation_degrees,
        ) = get_wrnch_data(image_byte_stream=binary_image)
        resized_matrix = get_resize(
            filename=operation_file_path,
            image_matrix=None,
            height_change_factor=left_wrist_displ,
            width_change_factor=right_wrist_displ,
            show_image=False,
        )
        get_rotation(
            file_path=None,
            image_matrix=resized_matrix,
            rotation_angle=rotation_degrees,
            show_image=False,
            result_file_name=file_name,
        )
        sizing = wrist_dist - shoulder_dist
        if sizing > 0:
            response_text = "Image is enlarged "
        elif sizing == 0:
            response_text = "Image is of same size "
        else:
            response_text = "Image is shrinked "
        response_text = f"{response_text}with angle={rotation_degrees}"
        message_twilio.media(f"{HOST_URL}/result_images/{file_name}")

    else:
        response_text = "No image is received!!"
    message_twilio.body(response_text)

    response.append(message_twilio)

    return str(response)
