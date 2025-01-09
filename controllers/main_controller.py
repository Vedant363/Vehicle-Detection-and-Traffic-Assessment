from functools import wraps
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, session, send_file
from models.forms import LoginForm, URLForm
from models.sheets import get_cached_data, initialize_google_sheets, global_sheet
from models.youtube_stream import extract_video_id, global_video_id
from models.decryption import check_decryption_status

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def url_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'url_entered' not in session:
            return redirect(url_for('main.passfunc'))
        return f(*args, **kwargs)
    return decorated_function

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if not check_decryption_status():
            return render_template('error_page.html', message="Decryption failed or credentials not found."), 500

        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            if username == "test" and password == "test123":
                flash('✅ Login successful!', 'success')
                session['logged_in'] = True
                return redirect(url_for('main.passfunc'))
            else:
                flash('❌ Invalid username or password', 'danger')
                form.username.data = ''
                form.password.data = ''
        return render_template('login_form.html', form=form)
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /login"), 500
    
@main_bp.route('/e')
@login_required
def passfunc():
    session.pop('_flashes', None)
    return redirect(url_for('main.home'))

@main_bp.route('/enterrurl')
@login_required
def home():
    try:
      form = URLForm()
      session['url_entered'] = True
      return render_template('youtube_url_entry.html', form=form)
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /enterurl"), 500

@main_bp.route('/submit', methods=['GET', 'POST'])
@login_required
@url_required
def submit():
    try:
        form = URLForm()
        if form.validate_on_submit():
            youtube_url = form.youtube_url.data
            video_id = extract_video_id(youtube_url)
            if video_id:
                global global_video_id
                global_video_id = video_id
                return redirect(url_for('main.dashboard'))
            else:
                flash("❌ Invalid YouTube URL", "danger")
                return redirect(url_for('main.home'))
        else:
            flash("❌ Invalid YouTube URL!!", "danger")
            flash("💡 Use default URL or Enter valid URL", "suggestion")
            return redirect(url_for('main.home'))
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /submit"), 500

@main_bp.route('/index')
@login_required
@url_required
def dashboard():
    try:
        global global_sheet
        if global_sheet is None:
            global_sheet = initialize_google_sheets('vehicle-detection')

        rows = get_cached_data()
        if not rows:
            rows = []
        return render_template('dashboard.html', data=rows)
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /index"), 500

@main_bp.route('/traffic_data')
@login_required
@url_required
def traffic_data():
    try:
        from models.tracking import traffic_analysis_data
        analysis_data_serializable = {
            'vehicle_count': int(traffic_analysis_data.get('vehicle_count', 0)),
            'avg_speed': float(traffic_analysis_data.get('avg_speed', 0.0)),
            'is_traffic_jam': bool(traffic_analysis_data.get('is_traffic_jam', False)),
            'too_many_heavy_vehicles': bool(traffic_analysis_data.get('too_many_heavy_vehicles', False)),
            'estimated_clearance_time': float(traffic_analysis_data.get('estimated_clearance_time', 0.0)),
            'traffic_light_decision': traffic_analysis_data.get('traffic_light_decision', ["Red", 30])
        }
        return analysis_data_serializable
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /traffic_data"), 500

@main_bp.route('/get_chart_data')
@login_required
@url_required
def get_chart_data():
    try:
        rows = get_cached_data()
        classLabels = {}
        timeData = {}
        roadOccupancy = {}

        for row in rows:
            timestamp = row['Timestamp']
            classLabel = row['Class Name']
            width = float(row['Width'])
            height = float(row['Height'])
            area = width * height

            classLabels[classLabel] = classLabels.get(classLabel, 0) + 1
            timeKey = timestamp.split()[0][:5]
            timeData[timeKey] = timeData.get(timeKey, 0) + 1
            roadOccupancy[classLabel] = roadOccupancy.get(classLabel, 0) + area

        return {
            'classLabels': {'keys': list(classLabels.keys()), 'values': list(classLabels.values())},
            'timeData': {'keys': list(timeData.keys()), 'values': list(timeData.values())},
            'roadOccupancy': {'keys': list(roadOccupancy.keys()), 'values': list(roadOccupancy.values())}
        }
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /get_chart_data"), 500
    
data1 = None

@main_bp.route('/final_page', methods=['GET','POST'])
@login_required
@url_required
def stop_execution():
    try:
        from models.state import StopExecution
        StopExecution.set_stop_execution_status(True)
        global global_sheet
        if global_sheet is None:
            global_sheet = initialize_google_sheets('vehicle-detection')
        rows = get_cached_data()
        if not rows:
            rows = []
        
        from models.sheets import fetch_data_from_sheets
        global data1
        data1 = fetch_data_from_sheets()

        if len(data1) > 2:
            return render_template('dashboard2.html', data=rows, data1=data1)
        else:
            from models.sheets import clear_google_sheets_data
            clear_google_sheets_data('vehicle-detection', 'Sheet1')
            return render_template('error_page.html', message='No detections were made'), 500
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /final_page"), 50

@main_bp.route('/download_csv', methods=['GET'])
@login_required
@url_required
def download_csv():
    try:
        from models.sheets import write_to_csv
        global data1
        if data1:
            csv_file_path = write_to_csv(data1)
            data1 = None
            from models.sheets import clear_google_sheets_data
            clear_google_sheets_data('vehicle-detection', 'Sheet1')

        return send_file(csv_file_path, as_attachment=True, download_name='data.csv'), 200
    except Exception as e:
        return render_template('error_page.html', message=f"Error generating CSV: {str(e)}"), 500
    
@main_bp.route('/complete_stop', methods=['GET','POST'])
@login_required
@url_required
def call_complete_stop():
    try:
        from models.tracking import complete_stop
        session.clear()
        from models.sheets import clear_google_sheets_data
        clear_google_sheets_data('vehicle-detection', 'Sheet1')
        complete_stop()
        return jsonify(message="Execution stopped successfully. You can close this page now!!"), 200
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /complete_stop"), 500
    
@main_bp.route('/test')
@login_required
def hi():
    return jsonify(message="OK"), 200

@main_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    flash('☑️ You have been logged out!', 'success')
    return redirect(url_for('main.login'))