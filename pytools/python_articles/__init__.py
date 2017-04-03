from flask import Blueprint


python_articles = Blueprint('python_articles', __name__, template_folder='templates', static_folder='static', url_prefix='/python_articles')

from . import views



