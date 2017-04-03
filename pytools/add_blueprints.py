import os

init_file = '''from flask import Blueprint


%s = Blueprint('%s', __name__, template_folder='templates', static_folder='static', url_prefix='/%s')

from . import views
'''
views_file = '''from . import %s
from flask import render_template


@%s.route('/')
def root():
    return 'to be continued...'
'''


while 1:
    name = input('Input the function name: ')
    if (os.path.exists(name)):
        print('%s is existed.' % name)
        continue
    try:
        os.mkdir(name)
        os.mkdir('%s/static' % name)
        os.mkdir('%s/templates' % name)
        with open('%s/static/.gitconfig' % name, 'w') as f:
            pass
        with open('%s/templates/.gitconfig' % name, 'w') as f:
            pass
        with open('%s/__init__.py' % name, 'w', encoding='utf-8') as f:
            f.write(init_file % (name, name, name))
        with open('%s/views.py' % name, 'w', encoding='utf-8') as f:
            f.write(views_file % (name, name))

        break
    except Exception as e:
        print(e)
