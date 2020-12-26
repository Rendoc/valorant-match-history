from flask import Flask, render_template, request, redirect, url_for
import json
from app.val_api import ValorantAPI
import time

app = Flask(__name__)

# Gives competitive movement, game outcome, and associated colors
match_movement_hash = {
    'INCREASE': ['Increase', 'Victory', 'green', 'rgba(52,211,153,1)'],
    'MINOR_INCREASE': ['Minor Increase', 'Victory', 'green', 'rgba(52,211,153,1)'],
    'MAJOR_INCREASE': ['Major Increase', 'Victory', 'green', 'rgba(52,211,153,1)'],
    'DECREASE': ['Decrease', 'Defeat', 'red', 'rgba(248,113,113,1)'],
    'MAJOR_DECREASE': ['Major Decrease', 'Defeat', 'red', 'rgba(248,113,113,1)'],
    'MINOR_DECREASE': ['Minor Decrease', 'Defeat', 'red', 'rgba(248,113,113,1)'],
    'PROMOTED': ['Promoted', 'Victory', 'green', 'rgba(52,211,153,1)'],
    'DEMOTED': ['Demoted', 'Defeat', 'red', 'rgba(248,113,113,1)'],
    'STABLE': ['Stable', 'Draw', 'gray', 'rgba(156, 163, 175, 1)']
}

# Gives map name
maps_hash = {
    '/Game/Maps/Duality/Duality': 'bind',
    '/Game/Maps/Bonsai/Bonsai': 'split',
    '/Game/Maps/Ascent/Ascent': 'ascent',
    '/Game/Maps/Port/Port': 'icebox',
    '/Game/Maps/Triad/Triad': 'haven',
    '': 'unknown'
}


@app.before_request
def before_request():
    scheme = request.headers.get('X-Forwarded-Proto')
    if scheme and scheme == 'http' and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@app.route('/')
def home():
    return render_template('login.html')

# Redirect people to login page


@app.route('/match_history', methods=['GET'])
def redirect_to_login():
    return redirect(url_for('home'))


@app.route('/match_history', methods=['POST'])
def display_match_history():
    username = request.form['username']
    password = request.form['password']
    region = request.form['region']

    # Attempt login
    try:
        valorant = ValorantAPI(username, password, region)
    except:
        print('A login error occurred. F')
        return render_template('error.html', error='Invalid username/password or incorrect region.')

    # Attempt to acquire match history data
    try:
        json_res = valorant.get_match_history()
    except:
        print('Cannot get match history.')
        return render_template('error.html', error='Cannot get match history.')

    # Attempt to parse through match history data
    try:
        posts = []
        for match in json_res['Matches']:
            # print(match)
            if match['CompetitiveMovement'] == 'MOVEMENT_UNKNOWN':
                continue
            match_movement, game_outcome, main_color, gradient_color = match_movement_hash[
                match['CompetitiveMovement']]
            lp_change = ''

            game_map = 'images/maps/' + maps_hash[match['MapID']] + '.png'

            tier = 'images/ranks/' + str(match['TierAfterUpdate']) + '.png'

            epoch_time = match['MatchStartTime'] // 1000
            date = time.strftime('%m-%d-%Y', time.localtime(epoch_time))

            before = match['TierProgressBeforeUpdate']
            after = match['TierProgressAfterUpdate']

            # calculate lp change, TODO: do this more efficiently
            if match['CompetitiveMovement'] == 'PROMOTED':
                lp_change = '+' + str(after + 100 - before)
            elif match['CompetitiveMovement'] == 'DEMOTED':
                lp_change = '-' + str(before + 100 - after)
            else:
                if before < after:
                    # won
                    lp_change = '+' + str(after - before)
                else:
                    # lost
                    lp_change = str(after - before)

            match_data = {
                'lp_change': lp_change,
                'current_lp': after,
                'game_outcome': game_outcome,
                'movement': match_movement,
                'tier': tier,
                'date': date,
                'game_map': game_map,
                'main_color': main_color,
                'gradient_color': gradient_color
            }

            posts.append(match_data)

        print(posts)
        return render_template('match_history.html', posts=posts, name=valorant.game_name, title='VALORANTELO - Match History')
    except:
        print('Error parsing match history data.')
        temp = json_res
        print('Match history failed with:', temp)
        return render_template('error.html', error='Error parsing match history data. An administrator will look into this. Try again soon.')
