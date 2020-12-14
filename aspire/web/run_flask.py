import sys
import os

sys.path.insert(0, os.path.abspath('..'))

# Run a test server.
from aspire.web import create_app

if __name__ == "__main__":
    create_app().run(host='0.0.0.0', port=8080, debug=True)
