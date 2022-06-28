import os

from src import app


if __name__ == '__main__':
    # Getting the port value from environment variable so port can be assigned by Heroku when deployed
    app.run('0.0.0.0', int(os.environ.get('PORT', 8000)), debug=True)
    