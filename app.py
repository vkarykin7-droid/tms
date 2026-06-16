from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'super_secret_football_key'

# --- 🌍 GLOBAL FOOTBALL DATABASE GENERATOR ---
LEAGUES_PROFILES = {
    "English Premier League": {"teams": ["Man Blue", "Man Red", "Liverpool V", "Arsenal L", "Chelsea B", "Tottenham H"], "avg_ovr": 82},
    "Spanish La Liga": {"teams": ["Madrid W", "Barcelona B", "Madrid R", "Sevilla F", "Valencia O"], "avg_ovr": 80},
    "Italian Serie A": {"teams": ["Milan R", "Milan B", "Turin B", "Napoli S", "Rome G"], "avg_ovr": 79},
    "German Bundesliga": {"teams": ["Munich R", "Dortmund Y", "Leverkusen B", "Leipzig R"], "avg_ovr": 79},
    "French Ligue 1": {"teams": ["Paris SG", "Marseille B", "Monaco R", "Lyon O"], "avg_ovr": 77},
    "Dutch Eredivisie": {"teams": ["Amsterdam A", "Eindhoven P", "Rotterdam F"], "avg_ovr": 74},
    "Portuguese Primeira Liga": {"teams": ["Lisbon S", "Lisbon B", "Porto D"], "avg_ovr": 74},
    "Saudi Pro League": {"teams": ["Riyadh Y", "Riyadh B", "Jeddah G", "Jeddah Y"], "avg_ovr": 76},
    "American MLS": {"teams": ["Miami P", "Los Angeles G", "New York C", "Atlanta U"], "avg_ovr": 71},
    "Brasileiro Série A": {"teams": ["Sao Paulo R", "Rio de Janeiro F", "Belo Horizonte A"], "avg_ovr": 73}
}

FIRST_NAMES = ["Luka", "Kylian", "Erling", "Mohamed", "Kevin", "Marcus", "Pedri", "Jude", "Harry", "Bruno", "Robert", "Virgil", "Frenkie", "Antoine", "Lautaro", "Son", "Bukayo", "Gabriel", "Rodri", "Vinicius"]
LAST_NAMES = ["Smith", "Garcia", "Martinez", "Müller", "Silva", "Ferrari", "De Jong", "Dias", "Fernandes", "Jones", "Mbappe", "Haard", "Kane", "Bellingham", "Alvarez", "Goretzka", "Van Dijk", "Salah", "Sane", "Chiesa"]
POSITIONS = ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"]

def calculate_player_value(ovr, age):
    """Calculates a realistic market value using an exponential scale based on rating and age maturity."""
    if ovr < 60: return 50000
    base_val = (ovr - 55) ** 4.2 * 120
    # Premium for youth potential, discount for players past their prime (older than 30)
    if age < 22: base_val *= 1.4
    elif age > 31: base_val *= 0.5
    return int(round(base_val, -4)) # Round to nearest 10,000

def generate_global_market():
    players = []
    player_id = 1
    
    for league, profile in LEAGUES_PROFILES.items():
        for team in profile["teams"]:
            # Generate a realistic 22-player squad for every single team
            for _ in range(22):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                pos = random.choice(POSITIONS)
                age = random.randint(17, 36)
                
                # Base rating varies slightly depending on how elite the league profile is
                ovr_variance = random.randint(-6, 8)
                overall = clamp(profile["avg_ovr"] + ovr_variance, 60, 95)
                
                # Potential must be equal to or higher than current rating
                potential = clamp(overall + random.randint(0, 12), overall, 99)
                if age > 28: potential = overall # No growth potential for veteran players
                
                value = calculate_player_value(overall, age)
                
                players.append({
                    "id": player_id,
                    "name": f"{first} {last}",
                    "age": age,
                    "position": pos,
                    "overall": overall,
                    "potential": potential,
                    "league": league,
                    "club": team,
                    "value": value
                })
                player_id += 1
    return players

def clamp(n, minn, maxn):
    return max(min(n, maxn), minn)

# Initialize the massive global system database pool right on server boot
GLOBAL_PLAYERS_POOL = generate_global_market()

# --- 🚀 ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['nickname'] = request.form.get('nickname')
        session['role'] = request.form.get('role')
        
        role_budgets = {
            'club_president': 150000000,
            'player_agent': 250000,
            'scout': 75000,
            'head_coach': 0
        }
        session['budget'] = role_budgets.get(session['role'], 0)
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'nickname' not in session: return redirect(url_for('index'))
    
    role_titles = {
        'player_agent': 'Player Agent ⚽',
        'scout': 'Talent Scout 🔍',
        'club_president': 'Club President 🏆',
        'head_coach': 'Head Coach 🎯'
    }
    
    return render_template(
        'dashboard.html', 
        nickname=session['nickname'], 
        role=session['role'], 
        pretty_role=role_titles.get(session['role'], 'Pro'),
        budget=f"€{session['budget']:,}"
    )

@app.route('/market')
def market():
    if 'nickname' not in session: return redirect(url_for('index'))
    
    # Optional filtering: grab user search or league filters from the page UI
    selected_league = request.args.get('league', 'English Premier League')
    
    # Filter down our 2000+ database instantly to show the chosen league
    filtered_list = [p for p in GLOBAL_PLAYERS_POOL if p['league'] == selected_league]
    
    # Format the currencies to look clean
    formatted_players = []
    for p in filtered_list:
        p_copy = p.copy()
        p_copy['value_str'] = f"€{p['value']:,}" if p['value'] > 0 else "Free Agent"
        formatted_players.append(p_copy)

    return render_template(
        'market.html', 
        players=formatted_players, 
        role=session['role'], 
        leagues=LEAGUES_PROFILES.keys(),
        current_league=selected_league
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
