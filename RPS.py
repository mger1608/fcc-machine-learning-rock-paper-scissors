from collections import Counter
import random

# Track opponent type across rounds
opponent_type = None

def player(prev_play, opponent_history=[], my_history=[]):
    global opponent_type

    # Clear state on new game
    if not prev_play:
        opponent_history.clear()
        my_history.clear()
        opponent_type = None

    if prev_play:
        opponent_history.append(prev_play)

    # Mapping: what beats what
    ideal_response = {'P': 'S', 'R': 'P', 'S': 'R'}

    # -------------------------------------------- #
    # Opponent Detection Functions

    def looks_like_abbey():
        if len(my_history) < 6:
            return False
        
        hits, checked = 0, 0
        for i in range(1, len(my_history)):
            last_me = my_history[i-1]

            # Build the same markov table as abbey
            nxts = [my_history[j+1]
                    for j in range(i - 1)
                    if my_history[j] == last_me and j + 1 < len(my_history)]
            
            if not nxts:
                continue
            predicted_me = max(set(nxts), key=nxts.count)
            expected_abbey = ideal_response[predicted_me]
            if opponent_history[i] == expected_abbey:
                hits += 1
            checked += 1
            
        return checked >= 5 and hits / checked > 0.6
    
    
    def looks_like_quincy():
        return len(opponent_history) >= 5 and opponent_history[-5:] in [
            ['R', 'R', 'P', 'P', 'S'],
            ['R', 'P', 'P', 'S', 'R'],
            ['P', 'P', 'S', 'R', 'R']
        ]

    def looks_like_mrugesh():
        if len(my_history) < 10:
            return False
        freq = Counter(my_history[-10:])
        return freq.most_common(1)[0][1] >= 6

    def looks_like_kris():
        if len(my_history) < 1 or len(opponent_history) < 1:
            return False
        return opponent_history[-1] == ideal_response.get(my_history[-1], None)


    # Detect opponent type once
    if opponent_type is None and len(opponent_history) >= 10:
        if looks_like_quincy():
            opponent_type = 'quincy'

        elif looks_like_kris():
            opponent_type = 'kris'

        elif looks_like_abbey():
            opponent_type = 'abbey'

        elif looks_like_mrugesh():
            opponent_type = 'mrugesh'

        else:
            opponent_type = 'unknown'

    # -------------------------------------------- #
    # Strategy Dispatch

    if opponent_type == 'quincy':
        my_guess = ideal_response.get(prev_play, 'R')

    elif opponent_type == 'kris':
        if len(my_history) >= 1:
            countered_move = ideal_response.get(my_history[-1], 'R')
            my_guess = ideal_response.get(countered_move, 'R')
        else:
            my_guess = random.choice(['R', 'P', 'S'])

    elif opponent_type == 'mrugesh':
        if len(my_history) >= 10:
            common_move = Counter(my_history[-10:]).most_common(1)[0][0]
        else:
            common_move = 'R'
        predicted = ideal_response.get(common_move, 'R')
        my_guess = ideal_response.get(predicted, 'R')

    elif opponent_type == 'abbey':
        if my_history:
            last_me = my_history[-1]
            seq = [my_history[i+1] for i in range(len(my_history) - 1) if my_history[i] == last_me]
            
            predicted_me = max(set(seq), key=seq.count) if seq else random.choice(['R', 'P', 'S'])
            abbey_play = ideal_response[predicted_me]
            my_guess = ideal_response[abbey_play]


    else:
        # Unknown or not enough data
        if len(opponent_history) < 3:
            my_guess = random.choice(['R', 'P', 'S'])
        else:
            last_two = tuple(opponent_history[-2:])
            freq = {'R': 0, 'P': 0, 'S': 0}
            for i in range(len(opponent_history) - 2):
                if tuple(opponent_history[i:i+2]) == last_two:
                    freq[opponent_history[i+2]] += 1
            if sum(freq.values()) > 0:
                likely = max(freq, key=freq.get)
                my_guess = ideal_response.get(likely, 'R')
            else:
                my_guess = random.choice(['R', 'P', 'S'])

    my_history.append(my_guess)
    return my_guess
