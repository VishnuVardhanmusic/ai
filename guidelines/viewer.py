from flask import Flask, render_template, request, redirect, url_for
import json
import os
import logging
logger = logging.getLogger(__name__)

app = Flask(__name__)
GUIDELINE_PATH = os.path.join(os.path.dirname(__file__), "guidelines.json")


# Load guidelines from JSON
def load_guidelines():
    logger.info("Loading guidelines from %s", GUIDELINE_PATH)
    with open(GUIDELINE_PATH, "r") as f:
        return json.load(f)


# Save updated list to JSON
def save_guidelines(data):
    logger.info("Saving %d guidelines to %s", len(data), GUIDELINE_PATH)
    with open(GUIDELINE_PATH, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    guidelines = load_guidelines()
    return render_template("index.html", guidelines=guidelines)


@app.route("/add", methods=["POST"])
def add():
    guidelines = load_guidelines()
    new_id = f"G{len(guidelines)+1:03d}"
    new_entry = {
        "id": new_id,
        "rule": request.form["rule"],
        "severity": request.form["severity"],
        "category": request.form["category"],
        "description": request.form["description"],
        "example": request.form["example"]
    }
    guidelines.append(new_entry)
    save_guidelines(guidelines)
    logger.info("Added new guideline %s - %s", new_id, new_entry["rule"])
    return redirect(url_for("index"))


@app.route("/delete/<guideline_id>")
def delete(guideline_id):
    guidelines = load_guidelines()
    guidelines = [g for g in guidelines if g["id"] != guideline_id]
    save_guidelines(guidelines)
    logger.warning("Deleting guideline: %s", guideline_id)
    return redirect(url_for("index"))


@app.route("/edit/<guideline_id>", methods=["GET", "POST"])
def edit(guideline_id):
    guidelines = load_guidelines()
    entry = next((g for g in guidelines if g["id"] == guideline_id), None)

    if request.method == "POST":
        entry["rule"] = request.form["rule"]
        entry["severity"] = request.form["severity"]
        entry["category"] = request.form["category"]
        entry["description"] = request.form["description"]
        entry["example"] = request.form["example"]
        save_guidelines(guidelines)
        logger.info("Updating guideline: %s", guideline_id)
        return redirect(url_for("index"))

    return render_template("edit.html", entry=entry)



if __name__ == "__main__":
    app.run(debug=True)

