import os

from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import VisualRecognitionV3

from constants import DEFAULT_SERVICE_URL, THRESHOLD

load_dotenv(verbose=True)
IBM_API_KEY = os.environ.get("IBM_API_KEY")


def get_image_classification(
        image_url=None, image_binary_file=None, image_filename=None, threshold=THRESHOLD
):
    authenticator = IAMAuthenticator(IBM_API_KEY)
    visual_recognition = VisualRecognitionV3(
        version="2018-03-19", authenticator=authenticator
    )

    visual_recognition.set_service_url(DEFAULT_SERVICE_URL)

    classes_result = visual_recognition.classify(
        url=image_url,
        images_file=image_binary_file,
        images_filename=image_filename,
        threshold=threshold,
    ).get_result()
    classes_list = (
        classes_result.get("images", [{}])[0].get("classifiers", [{}])[0].get("classes")
    )

    if not classes_list:
        return []
    classes_list = list(map(lambda x: f"{x.get('class')}:{x.get('score')}", classes_list))
    return classes_list


if __name__ == "__main__":
    image_url = "https://ibm.biz/BdzLPG"
    print(get_image_classification(image_url=image_url))
