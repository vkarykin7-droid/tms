from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_football_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['nickname'] = request.form.get('nickname')
        session['role'] = request.form.get('role')
        # REDIRECT to the dashboard page instead of returning plain text
        return redirect(url_for('dashboard'))
    
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # SECURITY: If someone tries to go straight to /dashboard without logging in, boot them out
    if 'nickname' not in session or 'role' not in session:
        return redirect(url_for('index'))
    
    nickname = session['nickname']
    role = session['role']
    
    # Map technical names to pretty names for the UI
    role_titles = {
        'player_agent': 'Player Agent ⚽',
        'scout': 'Talent Scout 🔍',
        'club_president': 'Club President 🏆',
        'head_coach': 'Head Coach 🎯'
    }
    pretty_role = role_titles.get(role, 'Football Professional')

    return render_template('dashboard.html', nickname=nickname, role=role, pretty_role=pretty_role)

@app.route('/logout')
def logout():
    # Clear the session data when logging out
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
