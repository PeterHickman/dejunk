import sys

from flask import Flask, render_template, request, redirect, url_for

from lib.database_wrapper import DatabaseWrapper

app = Flask(__name__)
app.config.from_pyfile('settings.py')

db = DatabaseWrapper(app.config['CONNECTION_STRING'])


def get_page(req):
    if 'page' in req.args:
        return int(req.args.get('page'))
    elif 'page' in req.form:
        return int(req.form['page'])
    else:
        return 1


@app.route('/')
def status():
    totals = db.status_information()
    return render_template('status.html', selected_menu='status', totals=totals)


@app.route('/dejunk', methods=['GET', 'POST'])
def dejunk():
    if request.method == 'POST':
        page = db.classify_unknown(request.form)
    else:
        page = get_page(request)

    data = db.photos_with_status('unknown', app.config['IMAGES_A_PAGE'], app.config['IMAGES_A_ROW'], page)
    return render_template('dejunk.html', selected_menu='dejunk', data=data)


@app.route('/purge', methods=['GET', 'POST'])
def purge():
    if request.method == 'POST':
        page = db.photos_to_delete(request.form)
    else:
        page = get_page(request)

    data = db.photos_with_status('junk', app.config['IMAGES_A_PAGE'], app.config['IMAGES_A_ROW'], page)
    return render_template('purge.html', selected_menu='purge', data=data)


@app.route('/tags/')
@app.route('/tags/<tag>')
def tags(tag=None):
    if tag is None:
        tags = db.all_tags_and_counts()
        return render_template('tags.html', selected_menu='tags', tags=tags)
    else:
        page = get_page(request)

        data = db.photos_by_tags(tag, app.config['IMAGES_A_PAGE'], app.config['IMAGES_A_ROW'], page)
        return render_template('selected_tags.html', selected_menu='tags', data=data)


@app.route('/add_tags', methods=['POST'])
def add_tags():
    db.add_tags_to_photos(request.form)

    page = get_page(request)

    if ',' in request.form['id']:
        # Multiple images
        return redirect(url_for('tags', tag=request.form['query'], page=page))
    else:
        # Single image
        return redirect(url_for('picture', photo_id=request.form['id'], view=request.form['query'], page=page))

@app.route('/remove_tag')
def remove_tag():
    db.remove_tag_from_photo(request.args['photo_id'], request.args['old_tag'])

    page = get_page(request)

    return redirect(url_for('picture', photo_id=request.args['photo_id'], view=request.args['query'], page=page))


@app.route('/picture/<photo_id>')
def picture(photo_id):
    data = {}
    data['page'] = get_page(request)
    data['query'] = request.args['view']
    data['photo'] = db.get_picture(photo_id)
    data['tags'] = db.all_tags_for_photo(photo_id)

    return render_template('picture.html', selected_menu='picture', data=data)


@app.route('/admin')
def admin():
    return render_template('holding_page.html', selected_menu='admin', text='ADMIN')
