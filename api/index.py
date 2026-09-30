import os
import sys

# Add project root to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app as flask_app

class VercelWSGIWrapper:
    """
    WSGI wrapper ensuring that request paths on Vercel match Flask routes.
    Vercel sets HTTP_X_MATCHED_PATH with the original request path, or rewrites
    the PATH_INFO. We ensure PATH_INFO is cleanly set.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        x_matched = environ.get("HTTP_X_MATCHED_PATH", "")
        path_info = environ.get("PATH_INFO", "")

        if x_matched:
            clean_matched = x_matched.split("?")[0]
            environ["PATH_INFO"] = clean_matched
        elif path_info:
            if not path_info.startswith("/"):
                environ["PATH_INFO"] = "/" + path_info

        return self.wsgi_app(environ, start_response)

app = VercelWSGIWrapper(flask_app)
