from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# Secret key is needed to secure user sessions (saving their character data)
app.secret_key = 'super_secret_football_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Grab the data from the HTML form
        nickname = request.form.get('nickname')
        role = request.form.get('role')
        
        # Save them in the browser session
        session['nickname'] = nickname
        session['role'] = role
        
        # For now, we just redirect to a temporary success page
        return f"Character Created! Welcome {nickname}, the new {role.replace('_', ' ').title()}!"
    
    # If it's a GET request, just display the selection screen
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
