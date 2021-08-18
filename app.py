from flask import Flask, render_template, request

from movieRecommendation import Recommendation
from textRank import textRank
from textToGraph import NER
import json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

# Movie Recommendation
@app.route("/movieRecommendation")
def movieRecommendation():
    return render_template("movieRecommendation.html")

@app.route("/movieRecommendation",methods=["POST"])
def MRTextInput():
    try:
        Output = Recommendation(request.form["movie"])
    except Exception as error:
        print(error)
        Output = ["Execution Failed"]
    return render_template("movieRecommendation.html",result=Output)

# Text Summarization
@app.route("/textSummarization")
def textSummarization():
    return render_template("textSummarization.html")

@app.route("/textSummarization",methods=["POST"])
def TextInput():
    try:
        print(request.form["NumberOfSentences"])
        Output = textRank(request.form["InputText"],int(request.form["NumberOfSentences"]))
    except:
        Output = ["Invalid Input"]
    return render_template("textSummarization.html",result=Output)

# Text to Graph
@app.route("/textToGraph")
def textToGraph():
    graph = {"nodes":[],"edges":[]}
    return render_template("textToGraph.html",graph = graph)

@app.route("/textToGraph",methods=["POST"])
def NERTextInput():
    try:
        graph = NER(request.form["InputText"])
        Output = "Success"
    except Exception as error:
        # print(error)
        graph = {"nodes":[],"edges":[]}
        Output = "Execution Failed"
    return render_template("textToGraph.html",result=Output,graph=graph)



if __name__ == "__main__":
    app.run(debug=True)
