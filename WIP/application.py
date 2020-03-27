import logging
import logging.handlers

import sheets_access as drive
from google_form import GOOGLE_FORM_URL

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
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



    # https://developer.mozilla.org/en-US/docs/Learn/Forms/Sending_and_retrieving_form_data
    # https://docs.plone.org/develop/plone/serving/http_request_and_response.html
    # http://wsgi.tutorial.codepoint.net/parsing-the-request-post
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    # When the method is POST the variable will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body)

    form_type = { "all":"Any Business Type",
                  "food":"Food",
                  "store":"Store",
                  "entertainment":"Entertainment",
                  "fitness":"Fitness",
                  "others":"Others" }
    ALL_FORM_TYPES = ["Art/Jewelry",
                      "Bakery",
                      "Bar",
                      "Bookstore",
                      "Cafe",
                      "Car Repairs",
                      "Clothing/Shoe Store",
                      "Electronics",
                      "Entertainment Venue",
                      "Florist",
                      "Gas Station",
                      "Groceries/Produce",
                      "Gym",
                      "Hardware Store",
                      "Homegoods",
                      "House Repairs",
                      "Restaurant",
                      "Salon/Haircuts",
                      "Outdoor Supplies"]
    site_type_map_to_form_types = {
                  "all":ALL_FORM_TYPES,
                  "food":["Bakery","Cafe","Groceries/Produce","Restaurant"],
                  "store":["Art/Jewelry",'Bookstore',"Clothing/Shoe Store",
                           "Electronics","Florist",'Homegoods',"Outdoor Supplies"],
                  "entertainment":["Entertainment Venue"],
                  "fitness":["Gym"],
                  "others":["Car Repairs","Gas Station","Bar","House Repairs",
                            "Salon/Haircuts"]
    }
    def get_selected_options(selected_type):
        selected_options = []
        for type in form_type:
            tuple = (type, "selected" if type == selected_type else "", form_type[type])
            selected_options.append(tuple)
        print(selected_options)
        return selected_options

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
                print(d)
                zip = d.get('zip',['91126'])[0]
                # this makes sure they dont type "City, State"
                city = (d.get('city',['Pasadena'])[0]).split(',')[0]
                type = d['type'][0]
                # type = d.get('type',['all'])
                drive_data = drive.run_sheets_scrape(zip, city, type, site_type_map_to_form_types)
                response = render_template('results.html',
                                           {'data': drive_data,
                                            'data_len': len(drive_data),
                                            'parent':'/static/',
                                            'form':GOOGLE_FORM_URL,
                                            'zip':zip,
                                            'city':city,
                                            'type':type,
                                            'options':get_selected_options(type)})

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
        elif '/business/' in path:
            row = path.split('business/')[-1]
            record = drive.get_row_record(int(row))
            print(record)
            response = render_template('listing.html', {'parent':'/static/',
                                                        'form':GOOGLE_FORM_URL})
                                                        # 'record':record})
        else:
            # passing in the static folder which contains the static resources
            response = render_template('index.html', {'parent':'/static/',
                                                      'form':GOOGLE_FORM_URL,
                                                      'options':get_selected_options('all')})
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
