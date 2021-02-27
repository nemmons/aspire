import os, datetime

from flask import Flask, render_template, _app_ctx_stack, flash, redirect, url_for, send_file, request
from werkzeug.utils import secure_filename
from sqlalchemy.orm import scoped_session
from aspire.app.database.engine import ConnectionManager
from aspire.app.database.models import RatingStep, RatingStepType, RatingStepParameter, RatingManual, RatingVariable
from aspire.app.Rating import rate as rater_rate, rate_from_csv
from aspire.app.repository.RatingManualRepository import RatingManualRepository
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from re import match

def create_webapp(test_config=None):
    app = Flask(__name__, instance_relative_config=True,
                instance_path=os.path.abspath(os.path.dirname(__file__)) + '/instance')
    app.config['UPLOAD_FOLDER'] = app.instance_path + '/tmp/uploads'

    connection_manager = ConnectionManager()
    session_factory = connection_manager.get_session_factory()
    app.session = scoped_session(session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(app.instance_path + '/tmp/uploads', exist_ok=True)
    except OSError:
        import sys
        print("Unexpected error creating web directories:", sys.exc_info()[0])
        pass

    admin = Admin(app, name='Flask Rater Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(RatingManual, app.session))
    admin.add_view(ModelView(RatingStep, app.session))
    admin.add_view(ModelView(RatingStepType, app.session))
    admin.add_view(ModelView(RatingStepParameter, app.session))
    admin.add_view(ModelView(RatingVariable, app.session))

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/demo/seed-data')
    def seed_demo_data():
        from aspire.app.Demo import seed_demo_data
        seed_demo_data()
        flash('A sample rating manual has been populated into the database!')
        return redirect(url_for('index'))

    @app.route('/demo/generate-csv')
    def generate_demo_csv():
        from aspire.app.Demo import generate_demo_rating_input_csv
        timestamp = datetime.datetime.now().isoformat()
        path = app.instance_path + '/tmp/demo-' + timestamp + '.csv'

        generate_demo_rating_input_csv(path)
        return send_file(path, as_attachment=True, attachment_filename='demo_rating_input.csv')

    @app.route('/rating-manuals/<int:rating_manual_id>')
    def rating_manual(rating_manual_id: int):
        repository = RatingManualRepository(app.session)
        manual = repository.get(rating_manual_id)

        sub_risk_counts = {sub_risk: int(request.args.get(sub_risk, 1)) for sub_risk in manual.get_sub_risks()}
        return render_template('manual.html', manual=manual, rating_manual_id=rating_manual_id, sub_risk_counts=sub_risk_counts)

    @app.route('/rate/<int:rating_manual_id>', methods=['POST'])
    def rate(rating_manual_id: int):
        repository = RatingManualRepository(app.session)
        manual = repository.get(rating_manual_id)

        request_data = request.form.to_dict()
        inputs = {}

        for field, value in request_data.items():
            m = match(r"(\w+)\[(\d+)](\w+)", field)
            if m:
                sub_risk, loop_index, variable = m.group(1, 2, 3)
                if sub_risk not in inputs:
                    inputs[sub_risk] = []
                while len(inputs[sub_risk]) < int(loop_index)+1:
                    inputs[sub_risk].append({})
                inputs[sub_risk][int(loop_index)][variable] = value
                continue
            inputs[field] = value

        results = rater_rate(rating_manual_id, repository, inputs, report_detail=True)
        final_rate = results[-1]['rating_variables']['rate']
        return render_template('rate_results.html', manual=manual, rating_manual_id=rating_manual_id, results=results,
                               final_rate=final_rate)

    @app.route('/rating/csv', methods=['GET', 'POST'])
    def csv_rating():
        repository = RatingManualRepository(app.session)
        manuals = repository.list()
        if request.method == 'GET':
            return render_template('csv_rating.html', manuals=manuals)

        if 'file' not in request.files or (request.files['file'].filename == ''):
            flash('Please select a file!')
            return redirect(request.url)

        file = request.files['file']

        if not is_csv(file.filename):
            flash('CSVs only, please!')
            return redirect(request.url)

        timestamp = datetime.datetime.now().isoformat()
        unique_filename = file.filename.rsplit('.', 1)[0].lower() + '-' + timestamp + '.csv'
        return_filename = file.filename.rsplit('.', 1)[0].lower() + '-results.csv'

        dest_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename))
        file.save(dest_path)

        rate_from_csv(request.form['rating_manual_id'], dest_path)
        return send_file(dest_path, as_attachment=True, attachment_filename=return_filename)

    def is_csv(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

    return app
