# main.py
# Aritra Biswas, 2016
#
# Main Flask routines for lightcoin.

from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    return "test"

if __name__ == "__main__":
    app.run()
