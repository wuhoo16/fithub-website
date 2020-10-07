# BEFORE DOING ANYTHING IN PYCHARM CONSOLE: .\env\Scripts\activate
# TO RUN IN CONSOLE: python -m flask run

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Class for equipment object
class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# For making a new webpage
@app.route('/')
def index():
    return render_template('equipmentPage.html')

if __name__ == "__main__":
    app.run(debug=True)
