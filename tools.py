from config import db
import time

def add_log(content, user_id=-1):
    db.add_row('log', data={'content': content, 'user_id': user_id,\
            'time': time.time()})


