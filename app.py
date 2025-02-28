from flask import Flask, request, jsonify
from flask_cors import CORS
from textblob import TextBlob

app = Flask(__name__)
CORS(app)


@app.route('/rate', methods=['POST'])
def rate_statement():
    data = request.json
    statement = data.get('statement')
    blob = TextBlob(statement)
    sentiment = blob.sentiment

    if sentiment.subjectivity == 0:
        return jsonify(score=0, category="Neutral and professional language")
    elif 0 < sentiment.subjectivity <= 0.5:
        return jsonify(score=int(sentiment.subjectivity * 10), category="Slightly emotional or subjective language")
    elif sentiment.subjectivity > 0.5:
        return jsonify(score=int(sentiment.subjectivity * 10),
                       category="Highly charged, inflammatory, or manipulative language")


@app.route('/score', methods=['POST'])
def score_balance_of_perspectives():
    data = request.json
    statement = data.get('statement')

    viewpoint_keywords = ["however", "but", "on the other hand", "while", "although",
                          "yet", "still", "despite", "in contrast", "conversely",
                          "notwithstanding", "even though", "regardless", "whereas",
                          "on the contrary", "unlike", "in spite of",
                          "some employees argue", "other employees believe", "it is true that", "admittedly",
                          "from an employee's perspective", "from a management perspective",
                          "considering different viewpoints within the team",
                          "proponents of", "opponents of", "supporters of", "critics of",
                          "some suggest", "others recommend", "one school of thought is", "another perspective is",
                          "while some find it beneficial", "others find it challenging",  # More HR-specific phrasing
                          "the union argues", "management contends",  # For unionized environments
                          "from a legal standpoint", "from an ethical perspective",  # Important for HR
                          "regarding performance reviews", "concerning employee benefits",
                          "in terms of workplace culture",  # Contextual phrases
                          "with respect to work-life balance", "related to employee development",
                          # More context-specific phrases
                          "some feel that", "others express concern about",  # Phrases about employee sentiment
                          ]

    negative_keywords = ["everyone agrees", "unanimously agrees", "no one disagrees", "all agree",
                         "there is no debate about", "it's clear that", "undisputed fact",  # Added "undisputed fact"
                         "obviously", "clearly", "certainly", "without a doubt",  # Added words that often signal bias
                         ]

    sentences = statement.split('.')
    total_sentences = len(sentences)

    has_multiple_viewpoints = any(
        keyword.lower() in statement.lower() for keyword in viewpoint_keywords)  # Case-insensitive
    has_negative_keywords = any(neg_keyword.lower() in statement.lower() for neg_keyword in
                                negative_keywords)  # Case-insensitive negative keywords

    if has_multiple_viewpoints and total_sentences > 1 and not has_negative_keywords:  # Check for negative keywords
        return jsonify(score=0, category="Multiple viewpoints presented fairly")
    elif has_multiple_viewpoints and not has_negative_keywords:  # Check for negative keywords
        score = int(min(total_sentences * 2, 9))  # Cap score at 9
        return jsonify(score=score, category="Acknowledges other viewpoints but favors one")
    elif has_negative_keywords and total_sentences > 1:  # Prioritize negative keyword detection
        return jsonify(score=7, category="Presents multiple viewpoints, but with bias")  # New category and score
    elif has_negative_keywords:
        return jsonify(score=3, category="Strongly biased, dismissive of other viewpoints")  # New category and score
    else:
        return jsonify(score=10, category="Completely one-sided, ignoring other perspectives")
    data = request.json
    statement = data.get('statement')
    viewpoint_keywords = ["however", "but", "on the other hand", "while", "although",
                          "yet", "still", "despite", "in contrast", "conversely",
                          "notwithstanding", "even though", "regardless", "whereas",
                          "on the contrary", "unlike", "in spite of",
                          "some employees argue", "other employees believe", "it is true that", "admittedly",
                          "from an employee's perspective", "from a management perspective",
                          "considering different viewpoints within the team",
                          "proponents of", "opponents of", "supporters of", "critics of",
                          "some suggest", "others recommend", "one school of thought is", "another perspective is",
                          "while some find it beneficial", "others find it challenging",  # More HR-specific phrasing
                          "the union argues", "management contends",  # For unionized environments
                          "from a legal standpoint", "from an ethical perspective",  # Important for HR
                          "regarding performance reviews", "concerning employee benefits",
                          "in terms of workplace culture",  # Contextual phrases
                          "with respect to work-life balance", "related to employee development",
                          # More context-specific phrases
                          "some feel that", "others express concern about",  # Phrases about employee sentiment
                          ]

    sentences = statement.split('.')
    has_multiple_viewpoints = any(keyword in statement for keyword in viewpoint_keywords)
    total_sentences = len(sentences)

    if has_multiple_viewpoints and total_sentences > 1:
        return jsonify(score=0, category="Multiple viewpoints presented fairly")
    elif has_multiple_viewpoints:
        return jsonify(score=int(total_sentences * 2), category="Acknowledges other viewpoints but favors one")
    else:
        return jsonify(score=10, category="Completely one-sided, ignoring other perspectives")


@app.route('/credibility', methods=['POST'])
def assess_credibility():
    data = request.json
    statement = data.get('statement')
    credible_sources = ["academy of management journal", "journal of applied psychology",
                        "human resource management review", "gender, work & organization",
                        "harvard business review", "equal employment opportunity commission (eeoc) guidelines",
                        "department of labor (dol) resources", "society for human resource management (shrm)",
                        "world economic forum"]
    questionable_sources = ["unverified blogs and websites", "social media posts (without thorough verification)"]
    biased_sources = ["sources promoting discrimination"]

    statement_lower = statement.lower()

    # Check for known sources in the statement
    if any(source.lower() in statement_lower for source in credible_sources):
        return jsonify(score=0, category="Credible, neutral source with no known agenda")
    elif any(source.lower() in statement_lower for source in questionable_sources):
        return jsonify(score=3, category="Questionable credibility or potential bias")
    elif any(source.lower() in statement_lower for source in biased_sources):
        return jsonify(score=7, category="Known source of heavy bias or misinformation")
    else:
        return jsonify(score=5, category="Unknown source or unclear credibility")


@app.route('/factcheck', methods=['POST'])
def fact_check_statement():
    data = request.json
    statement = data.get('statement')

    # Keywords to identify fully factual statements
    factual_keywords = ["study", "report", "data", "evidence", "research"]
    questionable_keywords = ["suggest", "believe", "claim", "likely", "possibly"]
    misleading_keywords = ["false", "misleading", "fake", "untrue"]

    statement_lower = statement.lower()
    if any(keyword in statement_lower for keyword in factual_keywords):
        return jsonify(score=0, category="Fully factual, supported by reliable data")
    elif any(keyword in statement_lower for keyword in questionable_keywords):
        return jsonify(score=3, category="Cherry-picked evidence or questionable claims")
    elif any(keyword in statement_lower for keyword in misleading_keywords):
        return jsonify(score=7, category="Contains false/misleading information or no evidence")
    else:
        return jsonify(score=5, category="Unknown or unclear factual basis")


@app.route('/generalization', methods=['POST'])
def assess_generalization():
    data = request.json
    statement = data.get('statement')

    # Keywords to identify generalizations and stereotypes
    no_generalization_keywords = ["some", "many", "often", "occasionally"]
    overgeneralization_keywords = ["always", "never", "everyone", "nobody"]
    heavy_generalization_keywords = ["all", "none", "every", "everybody" "nobody"]

    statement_lower = statement.lower()
    if any(keyword in statement_lower for keyword in no_generalization_keywords):
        return jsonify(score=0, category="No generalizations or stereotypes")
    elif any(keyword in statement_lower for keyword in overgeneralization_keywords):
        return jsonify(score=3, category="Some overgeneralizations")
    elif any(keyword in statement_lower for keyword in heavy_generalization_keywords):
        return jsonify(score=7, category="Heavy use of stereotypes/generalizations")
    else:
        return jsonify(score=5, category="Moderate generalization")


import requests


@app.route('/analyze', methods=['POST'])
def analyze_bias():
    data = request.json
    statement = data.get('statement')

    if not statement:
        return jsonify(error="No statement provided"), 400

    try:
        # Call each scoring endpoint and log responses
        endpoints = ["rate", "score", "credibility", "factcheck", "generalization"]
        responses = {}

        for endpoint in endpoints:
            url = f'http://lucky9nueve.pythonanywhere.com/{endpoint}'
            response = requests.post(url, json={'statement': statement})

            if response.status_code != 200:
                return jsonify(error=f"Error calling {endpoint}: {response.text}"), 500

            responses[endpoint] = response.json()

        # Extract scores
        scores = {
            "languageTone": responses["rate"].get("score", 0),
            "balance": responses["score"].get("score", 0),
            "sourceCredibility": responses["credibility"].get("score", 0),
            "evidenceFactCheck": responses["factcheck"].get("score", 0),
            "generalizationCheck": responses["generalization"].get("score", 0),
        }

        # Calculate bias percentage
        total_bias_score = sum(scores.values())
        bias_percentage = (total_bias_score / 50) * 100

        return jsonify({
            "scores": scores,
            "biasPercentage": round(bias_percentage, 2)
        })

    except Exception as e:
        return jsonify(error=f"Exception: {str(e)}"), 500


if __name__ == '__main__':
    app.run(debug=True)
