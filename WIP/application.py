import logging
import logging.handlers

import sheets_access as drive
from google_form import GOOGLE_FORM_URL

from wsgiref.simple_server import make_server
from wsgi_static_middleware import StaticMiddleware
import os

# https://jinja.palletsprojects.com/en/2.11.x/api/#basics
from jinja2 import Environment, PackageLoader, select_autoescape
# set up an environment to use HTML in 'templates/' for 'application.py'
env = Environment(
    loader=PackageLoader('application', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler
LOG_FILE = '/opt/python/log/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

# function to render HTML templates
def render_template(filename, substitutions):
    # produce a template for the filename
    template = env.get_template(filename)
    # render the template using a dictionary of substitutions
    return str(template.render(substitutions))

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    if method == 'POST':
        response = ''
        try:
            # if path == '/':
            #     request_body_size = int(environ['CONTENT_LENGTH'])
            #     request_body = environ['wsgi.input'].read(request_body_size).decode()
            #     logger.info("Received message: %s" % request_body)
            # elif path == '/scheduled':
            #     logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'], environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
            if path == '/' or '/index':
                # this is eventually how we will process the search bar:
                # for now, we just link to the results page (without any param)
                # passing in the sheets data (eventually will have more params)
                print('should be returning results now!')
                response = render_template('results.html',
                                           {'data': drive.run_sheets_scrape(),
                                            'parent':'/static/',
                                            'form':GOOGLE_FORM_URL})

        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
    else:
        response = None
        if path == '/admin':
            response = render_template('admin.html', {'parent':'/static/',
                                                        'form':GOOGLE_FORM_URL})
        elif path == '/about':
            response = render_template('about.html', {'parent':'/static/',
                                                        'form':GOOGLE_FORM_URL})
        else:
            # passing in the static folder which contains the static resources
            response = render_template('index.html', {'parent':'/static/',
                                                      'form':GOOGLE_FORM_URL})
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]

# https://pypi.org/project/wsgi-static-middleware/
# this is what allows us to serve static resources (like CSS and JS)
BASE_DIR = os.path.dirname(__name__)
STATIC_DIRS = [os.path.join(BASE_DIR, 'static')]
application = StaticMiddleware(application, static_root='static', static_dirs=STATIC_DIRS)

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
