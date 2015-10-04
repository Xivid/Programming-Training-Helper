import sae
from SSECTA import wsgi
application = sae.create_wsgi_app(wsgi.application)