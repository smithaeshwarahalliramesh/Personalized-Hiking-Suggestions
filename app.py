from flask import Flask, request, render_template
import recommender_system

app = Flask(__name__)

@app.route("/")
def main():
    hikes = recommender_system.getHikeList()
    return render_template('index_new1.html', hikeList=hikes)

@app.route('/', methods=["POST"])
def recommender():
    hike = request.form['hike_name']
    recs = recommender_system.recommendation(hike)
    return render_template('recommender_new2.html', recList = recs)

if __name__ == "__main__":
    app.run()
