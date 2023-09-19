import hashlib
import sqlite3

db_connect = sqlite3.connect("robo_advisor_database.db")
db_cursor = db_connect.cursor()


# gets user_id from username
def get_user_id(user):
    db_cursor.execute("SELECT user_id FROM users WHERE username = ?", [user])
    user_id = (db_cursor.fetchall())[0][0]

    return user_id


# checks user's login details with provided parameters to grant access to their account
def login_connect(username, password):
    password = password.encode()
    password = hashlib.sha256(password).hexdigest()

    db_cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (str(username), str(password)))
    valid = db_cursor.fetchall()

    if valid:
        return True
    else:
        return False


# registers a new user account
def register_connect(username, password, api, secret):
    password = password.encode()
    new_pass = hashlib.sha256(password).hexdigest()
    new_user = username

    db_cursor.execute("SELECT user_id FROM users WHERE username = (?) OR api_key = (?)", (str(new_user), str(api)))
    valid = db_cursor.fetchall()

    if valid:
        return False
    else:
        db_cursor.execute("INSERT INTO users (username, password, api_key, secret_key) VALUES (?, ?, ?, ?)",
                          (str(new_user), str(new_pass), str(api), str(secret)))
        db_connect.commit()

        user_id = get_user_id(new_user)
        db_cursor.execute("INSERT INTO userinfo (budget, stop_loss, user_id) VALUES (?, ?, ?)",
                          (1000, 20, int(user_id)))
        db_connect.commit()
        return True


# retrieves user's API keys
def api_connect(user):
    db_cursor.execute("SELECT api_key, secret_key FROM users WHERE username = (?)", [user])
    get_api = db_cursor.fetchall()
    if get_api:
        api, secret = get_api[0][0], get_api[0][1]
        return api, secret
    else:
        return 0, 0


# adds user budget info when change is requested in UI
def add_budget(budget, username):
    user_id = get_user_id(username)
    db_cursor.execute("UPDATE userinfo SET budget = (?) WHERE user_id = (?)", (budget, user_id))
    db_connect.commit()


# adds user stop_loss info when change is requested in UI
def add_stop_loss(stop_loss, username):
    user_id = get_user_id(username)
    db_cursor.execute("UPDATE userinfo SET stop_loss = (?) WHERE user_id = (?)", (stop_loss, user_id))
    db_connect.commit()


# gets user's budget and stop_loss
def get_trade_data(username):
    user_id = get_user_id(username)
    db_cursor.execute("SELECT budget, stop_loss FROM userinfo WHERE user_id = (?)", [user_id])
    trade_info = db_cursor.fetchall()
    budget, stop_loss = trade_info[0][0], trade_info[0][1]

    return budget, stop_loss


# gets user's decision to allow trailing stop orders to be opened or not
def get_trail(username):
    user_id = get_user_id(username)
    db_cursor.execute("SELECT trail FROM userinfo WHERE user_id = (?)", [user_id])
    trail_info = db_cursor.fetchall()

    return trail_info[0][0]


# change user's decision to allow trailing stop orders
def change_trail(trail, username):
    user_id = get_user_id(username)
    db_cursor.execute("UPDATE userinfo SET trail = (?) WHERE user_id = (?)", (trail, user_id))
    db_connect.commit()


if __name__ == "__main__":
    db_cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,"
                      "username VARCHAR(255) NOT NULL,"
                      "password VARCHAR(255) NOT NULL,"
                      "api_key VARCHAR(255) NOT NULL,"
                      "secret_key VARCHAR(255) NOT NULL)")

    db_cursor.execute("CREATE TABLE IF NOT EXISTS userinfo (info_id INTEGER PRIMARY KEY,"
                      "budget INTEGER DEFAULT 1000,"
                      "stop_loss INTEGER DEFAULT 20,"
                      "trail CHAR(1) DEFAULT 'n',"
                      "user_id INTEGER NOT NULL,"
                      "FOREIGN KEY (user_id) REFERENCES users(user_id))")

    db_connect.commit()
