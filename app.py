from flask import Flask, render_template, request, redirect, url_for, Flask, \
    Response, session
from flask_bootstrap import Bootstrap
from config import S3_BUCKET, S3_KEY, S3_SECRET_ACCESS_KEY
from filters import datetimeformat, file_type
from flask import send_from_directory
import os
from resources import get_bucket, get_buckets_list, upload_file, \
    create_folder,\
        delete_folder, \
            rename_file, \
                    copy_to_bucket


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type

@app.route('/favicon.ico') 
def favicon():
    import os
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon') 
    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_buckets_list()
        return render_template("index.html", buckets=buckets)


@app.route('/files')
def files():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    Flask('File uploaded successfully')
    return redirect(url_for('files'))


@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    my_bucket = get_bucket()
    my_bucket.Object(key).delete()

    Flask('File deleted successfully')
    return redirect(url_for('files'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

@app.route('/rename', methods=['POST'])
def rename():            
    old_name = request.form['old_name']
    folder_name = request.form['folder_name']
    new_name = folder_name +"/"+ request.form['new_name']
    
    bucket_name = str(request.form['bucket_name'])
    rename_file(bucket_name,folder_name,new_name,old_name)
    return redirect(url_for('files', bucket_name= bucket_name,folder_name = folder_name))

@app.route('/copy', methods=['POST'])
def copyfile():       
    source_bucket = str(request.form['source_bucket'])
    folder_name = request.form['folder_name']
    source_key = request.form['source_key']
    other_bucket = request.form['other_bucket']
    otherkey = request.form['other_folder'] +"/" + request.form['otherkey']

    copy_to_bucket(source_bucket,source_key,other_bucket,otherkey)
    return redirect(url_for('files', bucket_name= source_bucket,folder_name = folder_name))


@app.route('/createfolder', methods=['POST'])
def createfolder():       
    bucket_name = str(request.form['bucket_name'])
    folder_name = request.form['folder_name'] + "/"
    create_folder(bucket_name,folder_name)
    return redirect(url_for('folders', bucket_name=bucket_name))

@app.route('/deletefolder', methods=['POST'])
def deletefolder():       
    bucket_name = str(request.form['bucket_name'])
    folder_name = request.form['folder_name']
    delete_folder(bucket_name,folder_name)
    return redirect(url_for('folders', bucket_name=bucket_name))

@app.route('/movefile', methods=['POST'])
def movefile():       
    source_bucket = str(request.form['source_bucket'])
    folder_name = request.form['folder_name']
    source_key = request.form['source_key']
    other_bucket = request.form['other_bucket']
    otherkey = request.form['otherkey']
    copy_to_bucket(source_bucket,source_key,other_bucket,otherkey)
    delete(source_bucket,source_key)
    return redirect(url_for('files', bucket_name= source_bucket,folder_name = folder_name))


if __name__ == "__main__":
    app.run()
