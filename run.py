import os

from dotenv import load_dotenv

from app import app

load_dotenv(verbose=True)

PORT = os.environ.get("PORT", 5000)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True, use_reloader=True)
