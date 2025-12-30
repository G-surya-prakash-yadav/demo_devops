from flask import Flask, render_template_string, request, send_file, redirect, url_for
import sqlite3
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from flask import Flask, render_template_string, request, send_file, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('court_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queries (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 case_type TEXT,
                 case_number TEXT,
                 filing_year TEXT,
                 timestamp TEXT,
                 raw_response TEXT,
                 parties TEXT,
                 filing_date TEXT,
                 hearing_date TEXT,
                 pdf_link TEXT
                 )''')
    conn.commit()
    conn.close()

init_db()

# PDF generator
def generate_pdf():
    file_path = "ravi_case_summary.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Case Summary: Ravi Kumar vs Me")

    # Body text
    c.setFont("Helvetica", 12)
    lines = [
        "Case Title      : Ravi Kumar vs Me",
        "Case Type       : Murder Case",
        "IPC Section     : 302 (Murder)",
        "Filing Date     : 2023-01-15",
        "Hearing Date    : 2025-08-10",
        "",
        "Summary:",
        "Ravi Kumar was arrested and charged under Section 302 IPC",
        "for allegedly being involved in a murder case that occurred",
        "in Hyderabad in early 2023. Based on the initial investigation,",
        "Ravi is suspected of fatally attacking the victim during a dispute.",
        "",
        "The case is currently in trial phase and the next hearing is",
        "scheduled for August 10, 2025. Further updates will be recorded",
        "as per court orders."
    ]

    y = height - 80
    for line in lines:
        c.drawString(50, y, line)
        y -= 20

    c.save()
    return file_path

# Main HTML + Bootstrap template with viewport meta tag for mobile responsiveness
template = """
<!DOCTYPE html>
<html>
<head>
    <title>Court Case Dashboard | RupsTech</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card shadow p-4">
            <h2 class="mb-4 text-primary text-center">📋 Indian Court Case Search (Murder)</h2>
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Case Type</label>
                    <select name="case_type" class="form-select" required>
                        <option value="">-- Select --</option>
                        <option value="Murder Case" {% if selected_case_type == "Murder Case" %}selected{% endif %}>Murder Case</option>
                        <option value="Civil" {% if selected_case_type == "Civil" %}selected{% endif %}>Civil</option>
                        <option value="Criminal" {% if selected_case_type == "Criminal" %}selected{% endif %}>Criminal</option>
                        <option value="W.P." {% if selected_case_type == "W.P." %}selected{% endif %}>W.P.</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Case Number</label>
                    <input type="text" name="case_number" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Filing Year</label>
                    <input type="text" name="filing_year" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Search Case</button>
            </form>

            {% if result %}
            <hr class="my-4">
            <h4 class="text-success">✅ Case Details Found</h4>
            <ul class="list-group mt-3">
                <li class="list-group-item"><strong>Parties:</strong> {{ result['parties'] }}</li>
                <li class="list-group-item"><strong>Filing Date:</strong> {{ result['filing_date'] }}</li>
                <li class="list-group-item"><strong>Next Hearing Date:</strong> {{ result['hearing_date'] }}</li>
                <li class="list-group-item"><strong>Order PDF:</strong> <a href="/download" class="btn btn-sm btn-success" download>Download Summary PDF</a></li>
            </ul>

            <div class="mt-4 text-center">
                <a href="{{ url_for('summary') }}" class="btn btn-info btn-lg">View Detailed Case Summary</a>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# HTML template for the summary page with viewport meta tag for mobile responsiveness
summary_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Case Summary | RupsTech</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="card shadow p-4">
            <a href="/" class="btn btn-secondary mb-4">← Back to Search</a>
            <h2 class="mb-4 text-primary text-center">📄 Detailed Case Summary</h2>

            <div class="row">
                <div class="col-md-6">
                    <ul class="list-group mt-3">
                        <li class="list-group-item"><strong>Case Title:</strong> {{ parties }}</li>
                        <li class="list-group-item"><strong>Case Type:</strong> Murder Case</li>
                        <li class="list-group-item"><strong>IPC Section:</strong> 302 (Murder)</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <ul class="list-group mt-3">
                        <li class="list-group-item"><strong>Filing Date:</strong> {{ filing_date }}</li>
                        <li class="list-group-item"><strong>Next Hearing Date:</strong> {{ hearing_date }}</li>
                        <li class="list-group-item"><strong>Case Status:</strong> Under Trial</li>
                    </ul>
                </div>
            </div>

            <hr class="my-4">

            <div class="mt-4">
                <h5>Summary of the Case</h5>
                <p>
                    This case involves Ravi Kumar, who has been arrested and charged under Section 302 of the Indian Penal Code (IPC).
                    The charge stems from an alleged murder that occurred in Hyderabad in early 2023.
                </p>
                <p>
                    Initial investigations suggest that Ravi Kumar was involved in a fatal altercation with the victim. The case is currently
                    in its trial phase, where evidence is being presented and examined by the court. The next hearing is scheduled for
                    {{ hearing_date }}.
                </p>
                <p>
                    The final judgment is still pending, and further developments will be added to the official court records as they occur.
                    This summary provides a preliminary overview based on the available information.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        case_type = request.form['case_type']
        case_number = request.form['case_number']
        filing_year = request.form['filing_year']

        # Simulated response data
        parties = "Ravi Kumar vs Me"
        filing_date = "2023-01-15"
        hearing_date = "2025-08-10"
        pdf_link = "/download"
        raw_html = "<html><body>Simulated HTML response</body></html>"

        # Save query
        conn = sqlite3.connect('court_data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO queries (case_type, case_number, filing_year, timestamp, raw_response,
                    parties, filing_date, hearing_date, pdf_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (case_type, case_number, filing_year, datetime.datetime.now().isoformat(),
                   raw_html, parties, filing_date, hearing_date, pdf_link))
        conn.commit()
        conn.close()

        result = {
            'parties': parties,
            'filing_date': filing_date,
            'hearing_date': hearing_date,
            'pdf_link': pdf_link
        }
        
        # Store the result in a global variable or session to access it on the summary page.
        # Note: A real-world app might use a database or session for this.
        app.case_result = result

        return render_template_string(template, result=result, selected_case_type=case_type)

    return render_template_string(template, result=None, selected_case_type="Murder Case")

@app.route('/summary')
def summary():
    # Retrieve the stored result. Handle the case where it doesn't exist.
    result = getattr(app, 'case_result', None)
    if not result:
        # If no case has been searched, redirect back to the home page.
        return redirect(url_for('home'))

    return render_template_string(
        summary_template,
        parties=result['parties'],
        filing_date=result['filing_date'],
        hearing_date=result['hearing_date']
    )

@app.route('/download')
def download_pdf():
    file_path = generate_pdf()
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
