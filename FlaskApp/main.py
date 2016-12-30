# main.py
# Aritra Biswas, 2016
#
# Main Flask routines for lightcoin.

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
