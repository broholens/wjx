"""
upload documents

"""
import os
import uuid
from flask import (Flask, request, url_for, render_template, flash)
from flask_uploads import (
    UploadSet, configure_uploads, DOCUMENTS, UploadNotAllowed
)

SECRET_KEY = 'zzzz'
app = Flask(__name__)
app.config.from_object(__name__)
UPLOAD_PATH = os.path.realpath('.') + '/uploads'
app.config['UPLOADED_DOCUMENTS_DEST'] = UPLOAD_PATH
app.config['UPLOADED_DOCUMENTS_ALLOW'] = DOCUMENTS
docs = UploadSet('documents')
configure_uploads(app, docs)


@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
    if request.method == 'POST':
        document = request.files.get('document')
        if not document:
            flash("请上传文件")
        else:
            try:
                filename = docs.save(document, name=uuid.uuid4().time+'.')
            except UploadNotAllowed:
                flash("不支持此类型文件")
            else:
                flash("上传成功")
    return render_template('uploads.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 5002)