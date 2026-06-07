users = set()

def register_user(user_id):

    users.add(user_id)

def users_count():

    return len(users)
