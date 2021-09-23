import math
import pandas as pd

def show_mouse(driver):
    driver.execute_script("""var seleniumFollowerImg=document.createElement('img');
    seleniumFollowerImg.setAttribute('src', 'data:image/png;base64,'
    + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
    + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
    + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
    + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
    + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
    + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
    + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
    + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
    + 'dAAAAABJRU5ErkJggg==');
    seleniumFollowerImg.setAttribute('id', 'selenium_mouse_follower');
    seleniumFollowerImg.setAttribute('style', 'position: absolute; z-index: 99999999999; pointer-events: none;');
    document.body.appendChild(seleniumFollowerImg);
    jQuery(document).mousemove(function(e){
    jQuery("#selenium_mouse_follower").css('left', e.pageX - 3);
    jQuery("#selenium_mouse_follower").css('top', e.pageY - 5);
    });""")

def clean_players(players):
    names = ['id', 'username', 'HP', 'class', 'mode_int', 'place', 'pos_x', 'pos_y', 'to_x', 'to_y', 'inertia_x', 'inertia_y']
    # formats = ['u4', 'U3', 'f8', 'U1', 'i', 'i', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8']

    buffer = pd.DataFrame(columns=names)

    for id, player in players.items():
        new_player = {
            'id': id,
            'username': player['username'],
            'HP': player['HP'],
            'class': player['class'],
            'mode_int': player['mode_int'],
            'place': player['place'],
            'pos_x': 0,
            'pos_y': 0,
            'to_x': 0,
            'to_y': 0,
            'inertia_x': 0,
            'inertia_y': 0,
        }

        if 'pos' in player and not pd.isnull(player['pos']):
            new_player['pos_x'] = player['pos']['x']
            new_player['pos_y'] = player['pos']['y']

        if 'to' in player and not pd.isnull(player['to']):
            new_player['to_x'] = player['to']['x']
            new_player['to_y'] = player['to']['y']

        if 'inertia' in player and not pd.isnull(player['inertia']):
            new_player['inertia_x'] = player['inertia']['x']
            new_player['inertia_y'] = player['inertia']['y']
        
        buffer = buffer.append(pd.DataFrame([tuple(new_player.values())], columns=names), ignore_index=True)
    
    return buffer

def clean_loots(loots):
    names = ['id', 'class', 'pos_x', 'pos_y', 'abouttodie']

    buffer = pd.DataFrame(columns=names)

    for id, loot in loots.items():
        new_loot = {
            'id': id,
            'class': loot['t'],
            'pos_x': 0,
            'pos_y': 0,
            'abouttodie': loot['abouttodie'],
        }

        if 'pos' in loot and not pd.isnull(loot['pos']):
            new_loot['pos_x'] = loot['pos']['x']
            new_loot['pos_y'] = loot['pos']['y']

        buffer = buffer.append(pd.DataFrame([tuple(new_loot.values())], columns=names), ignore_index=True)
    
    return buffer

def clean_gas_area(gas_area):
    return {
        'pos_x': gas_area['x'],
        'pos_y': gas_area['y'],
        'pos_r': gas_area['r'],
        'next_x': gas_area['next']['x'],
        'next_y': gas_area['next']['y'],
        'next_r': gas_area['next']['r'],
    }

def transform_class(c): # 'R', 'S', 'L'
    if c == 'L':
        return 0
    if c == 'P':
        return 1
    if c == 'R':
        return 2
    if c == 'S':
        return 3

def build_observation(our_player, players_df, loots_df, gas_area):
    our_player = our_player[['class', 'HP', 'pos_x', 'pos_y', 'to_x', 'to_y', 'inertia_x', 'inertia_y']]
    players_df = players_df[['class', 'HP', 'pos_x', 'pos_y', 'to_x', 'to_y', 'inertia_x', 'inertia_y']]

    players_df['class'] = players_df['class'].apply(lambda x: transform_class(x))
    our_player['class'] = transform_class(our_player['class'])

    loots_df = loots_df[['class', 'pos_x', 'pos_y', 'abouttodie']]

    loots_df['class'] = loots_df['class'].apply(lambda x: transform_class(x))

    return [
        our_player.to_list(),
        players_df.to_records(index=False).tolist(),
        loots_df.to_records(index=False).tolist(),
        list(clean_gas_area(gas_area).values())
    ]

# def calc_distance(e1, e2):
#     return math.sqrt(math.pow(e1['pos_x'] - e2['pos_x'], 2) + math.pow(e1['pos_y'] - e2['pos_y'], 2))

# def calc_angle(e1, e2):
#     return math.atan(e2['pos_y'] - e1['pos_y'] / e2['pos_x'] - e1['pos_x'])

# def calc_size(e):
#     return math.log2(max(20, e['HP'])) * 7.5
