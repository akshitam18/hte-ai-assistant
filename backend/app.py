from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from functools import wraps

app = Flask(__name__, template_folder='.')
CORS(app)  # Enables cross-origin requests for local testing
app.secret_key = 'super_secret_vjti_nexus_key_change_this_in_production'

# Hardcoded Admin Credentials
ADMIN_EMAIL = "admin@vjti.ac.in"
ADMIN_PASSWORD = "adminpassword123"  # Change this to your desired password

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Health Check Route for frontend status badge
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "message": "RAG Engine Active"}), 200

@app.route('/')
def login_page():
    # If already logged in as Admin, go straight to dashboard
    if session.get('user') == ADMIN_EMAIL:
        return redirect(url_for('dashboard_page'))
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    # 1. Check if user is the Admin
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session['user'] = email
        return jsonify({"success": True, "redirect": "/rag_dashboard.html"})

    # 2. Any other VJTI email gets redirected to Work in Progress
    elif email.endswith("@vjti.ac.in"):
        session['user'] = email
        return jsonify({"success": True, "redirect": "/work_in_progress.html"})

    # 3. Invalid domain or wrong admin credentials
    else:
        return jsonify({"success": False, "message": "Invalid credentials or unauthorized email domain."}), 401

@app.route('/rag_dashboard.html')
@login_required
def dashboard_page():
    # Security check: Non-admins trying to access the dashboard get sent to WIP
    if session.get('user') != ADMIN_EMAIL:
        return redirect(url_for('wip_page'))
    return render_template('rag_dashboard.html')

@app.route('/work_in_progress.html')
@login_required
def wip_page():
    return render_template('work_in_progress.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)