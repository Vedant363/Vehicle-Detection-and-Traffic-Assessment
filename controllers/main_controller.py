from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.forms import LoginForm, URLForm
from models.sheets import get_cached_data, initialize_google_sheets, global_sheet
from models.youtube_stream import extract_video_id, is_valid_youtube_url, global_video_id
from models.decryption import check_decryption_status

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
            # Dummy login
            if username == "test" and password == "test123":
                flash('✅ Login successful!', 'success')
                return redirect(url_for('main.passfunc'))
            else:
                flash('❌ Invalid username or password', 'danger')
                form.username.data = ''
                form.password.data = ''
        return render_template('login_form.html', form=form)
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /login"), 500
    
@main_bp.route('/e')
def passfunc():
    session.clear()
    return redirect(url_for('main.home'))

@main_bp.route('/enterrurl')
def home():
    try:
      form = URLForm()
      return render_template('youtube_url_entry.html', form=form)
    except Exception as e:
        return render_template('error_page.html', message=str(e) + " From: /enterurl"), 500

@main_bp.route('/submit', methods=['GET', 'POST'])
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
