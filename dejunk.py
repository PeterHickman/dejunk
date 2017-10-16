import sys

from flask import Flask, render_template, request, redirect, url_for

from lib.database_wrapper import DatabaseWrapper
import lib.tags as tag_tools

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
@app.route('/tags/<query>')
def tags(query=None):
    if query is None:
        query = db.all_tags_and_counts()
        return render_template('tags.html', selected_menu='tags', query=query)
    else:
        page = get_page(request)

        new_query = tag_tools.rewrite_query(query)

        if new_query == query:
            data = db.photos_by_tags(query, app.config['IMAGES_A_PAGE'], app.config['IMAGES_A_ROW'], page)

            return render_template('selected_tags.html', selected_menu='tags', data=data)
        else:
            ##
            # This redirect is just to clean up the url. It bugs me!
            ##
            return redirect(url_for('tags', query=new_query, page=page))


@app.route('/add_tags', methods=['POST'])
def add_tags():
    db.add_tags_to_photos(request.form)

    page = get_page(request)

    query = tag_tools.rewrite_query(request.form['query'])

    if ',' in request.form['id']:
        # Multiple images
        return redirect(url_for('tags', query=query, page=page))
    else:
        # Single image
        return redirect(url_for('picture', photo_id=request.form['id'], query=query, page=page))


@app.route('/remove_tag')
def remove_tag():
    db.remove_tag_from_photo(request.args['photo_id'], request.args['old_tag'])

    page = get_page(request)

    query = tag_tools.rewrite_query(request.args['query'])

    return redirect(url_for('picture', photo_id=request.args['photo_id'], query=query, page=page))


@app.route('/picture/<photo_id>')
def picture(photo_id):
    data = {}
    data['page'] = get_page(request)
    data['query'] = tag_tools.rewrite_query(request.args['query'])
    data['photo'] = db.get_picture(photo_id)
    data['tags'] = db.all_tags_for_photo(photo_id)

    return render_template('picture.html', selected_menu='picture', data=data)


@app.route('/admin')
def admin():
    return render_template('admin.html', selected_menu='admin', message=None)


@app.route('/convert_junk')
def convert_junk():
    count = db.convert_junk()
    message = "{} photos have been converted to junk status".format(count)
    return render_template('admin.html', selected_menu='admin', message=message)


@app.route('/remove_surplus')
def remove_surplus():
    count = db.remove_surplus()
    message = "{} surplus untagged tags have been removed".format(count)
    return render_template('admin.html', selected_menu='admin', message=message)
