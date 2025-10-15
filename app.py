from flask import Flask, render_template, request


# Create the Flask application
app = Flask(__name__)


def compute_gold_score(inputs: dict) -> tuple:
    """Compute the weighted gold attractiveness score and zone.

    Args:
        inputs (dict): Dictionary with numeric values (0-10) for each factor.

    Returns:
        tuple: (score (float), zone (str))
    """
    # Define weights matching the decision matrix (sum to 100)
    weights = {
        "real_rate": 25,
        "inflation": 15,
        "macro_stress": 15,
        "currency": 10,
        "central_banks": 10,
        "investor_flows": 10,
        "technical": 10,
        "supply": 5,
    }
    total_weight = sum(weights.values())

    # Compute the weighted score; each score is 0–10 and weight is percentage
    weighted_sum = 0.0
    contributions = {}
    for factor, weight in weights.items():
        value = inputs.get(factor, 0)
        # Normalize factor value (0-10) to (0-1) then multiply by weight
        contribution = (value / 10.0) * weight
        contributions[factor] = contribution
        weighted_sum += contribution

    # Scale to 0–100 by normalizing to the weight sum (should be 100)
    score = weighted_sum / total_weight * 100

    # Determine the zone based on the guidelines
    if score >= 70:
        zone = "Buy"
    elif 50 <= score < 70:
        zone = "Neutral / Accumulate"
    elif 30 <= score < 50:
        zone = "Hold / Underweight"
    else:
        zone = "Sell"
    return score, zone, contributions


@app.route("/", methods=["GET", "POST"])
def index():
    """Main landing page with form to input factor scores."""
    if request.method == "POST":
        # Retrieve and cast form values to floats
        factor_keys = [
            "real_rate",
            "inflation",
            "macro_stress",
            "currency",
            "central_banks",
            "investor_flows",
            "technical",
            "supply",
        ]
        inputs = {}
        for key in factor_keys:
            try:
                inputs[key] = float(request.form.get(key, 0))
            except (TypeError, ValueError):
                inputs[key] = 0.0
        # Compute score, zone and contribution breakdown
        score, zone, contributions = compute_gold_score(inputs)
        return render_template(
            "result.html",
            inputs=inputs,
            contributions=contributions,
            score=score,
            zone=zone,
        )
    return render_template("index.html")


if __name__ == "__main__":
    # When run directly, start the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)