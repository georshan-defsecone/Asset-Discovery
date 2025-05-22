from utils.server import app
from utils.logging_config import setup_logging

# Setup logging using centralized configuration
logger = setup_logging()

if __name__ == "__main__":
    try:
        logger.info("Starting Flask server...")
        app.run(debug=False, host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        print("\nServer stopped.")
