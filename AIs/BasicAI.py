import random

class BasicAI:

    def get_rel_move(self,state):
        rand = random.randint(0,2)
        moves = ['left','straight','right']
        print(rand)
        return moves[rand]
    
    def get_move(self,state):
        move = self.get_rel_move(state)

        if state.dirnx == 1:
            if move == 'left':
                return 'UP'
            elif move == 'straight':
                return 'RIGHT'
            else:
                return 'DOWN'
        elif state.dirnx == -1:
            if move == 'left':
                return 'DOWN'
            elif move == 'straight':
                return 'LEFT'
            else:
                return 'UP'
        elif state.dirny == 1:
            if move == 'left':
                return 'RIGHT'
            elif move == 'straight':
                return 'DOWN'
            else:
                return 'LEFT'
        else:
            if move == 'left':
                return 'LEFT'
            elif move == 'strtaight':
                return 'UP'
            else:
                return 'RIGHT'
