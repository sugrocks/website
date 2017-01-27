import os
import json
import crayons
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def gen_page(title, desc, file):
    # Main function
    print('Generating {}'.format(crayons.green(title)))

    if file == 'op.html':
        # If the file is the one for the OP, add the op template
        with open(os.path.join(THIS_DIR, 'templates', 'op.txt'), 'r') as op:
            optext = op.read()
            optext = optext.rstrip()
    else:
        optext = ''

    # Load the environment for the templates
    j2_env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'html')), trim_blocks=True)

    # Generate page
    j2_env.get_template(file).stream(
        pagetype='page-' + file.replace('.html', ''), pagename=title, pagedesc=desc,
        dategen=False, optext=optext)\
        .dump(os.path.join(THIS_DIR, 'public', file))


def gen_op_api():
    # Generate the op.json for the api
    data = {}

    # Get the OP template
    with open(os.path.join(THIS_DIR, 'templates', 'op.txt'), 'r') as op:
        optext = op.read()
        data["content"] = optext.rstrip()

    # Add our usual subject
    data['subject'] = '/sug/ - Steven Universe General'

    # Save it
    with open(os.path.join(THIS_DIR, 'api', 'op.json'), 'w') as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))


if __name__ == '__main__':
    # List of pages to generate
    gen_page('404', 'There\'s nothing here...', '404.html')
    gen_page('About', 'This website, the author and how to contact me', 'about.html')
    gen_page('OP Template', 'Copy/paste it, edit it and WE\'RE BACK BABY', 'op.html')
    gen_page('Random Media', '24/7 music and episodes', 'live.html')
    gen_page('Feedback', 'Yup, reading everything.', 'feedback.html')
    gen_page('New to Steven Universe', 'New to the show? Here\'s a little guide.', 'new-to-su.html')
    gen_page('Tumblr', '', 'tumblr.html')
    gen_op_api()
