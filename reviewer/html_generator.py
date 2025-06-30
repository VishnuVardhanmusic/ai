import json
from json2html import *
import os

OUTPUT_HTML = "outputs/review.html"
CSS_PATH = "static/styles.css"

def html_gen(path):
    if not os.path.isfile(path):
        print(f"❌ Error: {path} not found")
        return

    # Read JSON
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to HTML
    html_body = json2html.convert(json=data, table_attributes="class=\"table table-bordered\"")

    # Read CSS
    css_tag = ""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r") as css_file:
            css_content = css_file.read()
            css_tag = f"<style>\n{css_content}\n</style>"

    # Final HTML structure
    final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Review Report</title>
    {css_tag}
</head>
<body>
    <h1>🔍 Code Review Summary</h1>
    {html_body}
</body>
</html>
"""

    # Write output
    with open(OUTPUT_HTML, "w", encoding="utf-8") as out_file:
        out_file.write(final_html)

    print(f"✅ HTML review generated at {OUTPUT_HTML}")


