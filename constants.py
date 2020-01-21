import os

PARENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
RESULT_IMAGE_FOLDER = f"{PARENT_DIRECTORY}/result_images"
INPUT_IMAGE_FOLDER = f"{PARENT_DIRECTORY}/test_images"

THRESHOLD = 0.60
DEFAULT_SERVICE_URL = "https://gateway.watsonplatform.net/visual-recognition/api"
HOST_URL = "https://lazy-hands-api-heroku.herokuapp.com"
