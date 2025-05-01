import os
import re
import csv
import json
import io
import requests
import time
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

RECOMMENDATIONS = {
    "Sensitive Comment": "Remove any comments containing sensitive info before deploying.",
    "Hardcoded Secret": "Avoid hardcoding secrets. Use environment variables or secret managers.",
    "Insecure Error Message": "Avoid printing raw errors. Use logging libraries with proper levels."
}

def get_ai_recommendation(issue_type, code_snippet):
    prompt = f"""You are a security expert. A developer wrote the following line of code:

{code_snippet}

This was flagged as a '{issue_type}' issue.
Give one clear, practical recommendation to fix or improve the security of this code.
Be concise and relevant to the programming language if possible."""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://bassit-code.github.io",
                "X-Title": "SecureCodeScanner-FYP"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a secure code auditing assistant. Given a code snippet with a security vulnerability, explain the issue and recommend a fix."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.5
            },
            timeout=15
        )

        print("[RAW AI RESPONSE]", response.text)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"[OpenRouter AI ERROR] {e}")
        return RECOMMENDATIONS.get(issue_type, f"(AI recommendation unavailable: {e})")

def safe_get_ai_recommendation(issue_type, code_snippet, delay=False):
    if delay:
        time.sleep(1.2)
    return get_ai_recommendation(issue_type, code_snippet)

def traverse_directory(directory_path, file_extensions):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(tuple(file_extensions)):
                yield os.path.join(root, file)

def detect_sensitive_comments(file_path, delay=False):
    comment_keywords = ['TODO', 'FIXME', 'password', 'secret', 'key']
    sensitive_comments = []

    comment_patterns = [
        re.compile(r'#.*'),
        re.compile(r'//.*'),
        re.compile(r'/\*.*?\*/', re.DOTALL),
        re.compile(r'<!--(.*?)-->', re.DOTALL)
    ]

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern in comment_patterns:
            matches = pattern.findall(line)
            for match in matches:
                if any(keyword.lower() in match.lower() for keyword in comment_keywords):
                    recommendation = safe_get_ai_recommendation("Sensitive Comment", match.strip(), delay)
                    sensitive_comments.append((line_number, "Sensitive Comment", match.strip(), recommendation))

    if file_path.endswith(".json"):
        try:
            json_data = json.loads(''.join(lines))
            for key, value in json_data.items():
                if isinstance(value, str) and key.lower() in ["__comment", "_note", "comment"]:
                    if any(keyword.lower() in value.lower() for keyword in comment_keywords):
                        recommendation = safe_get_ai_recommendation("Sensitive Comment", value.strip(), delay)
                        sensitive_comments.append((1, "Sensitive Comment", f"{key}: {value.strip()}", recommendation))
        except json.JSONDecodeError:
            pass

    return sensitive_comments

def detect_hardcoded_secrets(file_path, delay=False):
    secret_pattern = re.compile(r"(password|pwd|api_key|access_token|secret|key|token|github_token|auth_token|client_secret)\s*=\s*['\"].+['\"]", re.IGNORECASE)
    hardcoded_secrets = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if secret_pattern.search(line):
                recommendation = safe_get_ai_recommendation("Hardcoded Secret", line.strip(), delay)
                hardcoded_secrets.append((line_number, "Hardcoded Secret", line.strip(), recommendation))
    return hardcoded_secrets

def detect_insecure_error_messages(file_path, delay=False):
    error_keywords = ['print', 'log', 'raise', 'traceback']
    insecure_errors = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if any(keyword in line.lower() for keyword in error_keywords):
                recommendation = safe_get_ai_recommendation("Insecure Error Message", line.strip(), delay)
                insecure_errors.append((line_number, "Insecure Error Message", line.strip(), recommendation))
    return insecure_errors

def save_report(results, output_format):
    if output_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['File', 'Line Number', 'Issue', 'Description', 'Recommendation'])
        for file_path, issues in results.items():
            for line_number, issue_type, description, recommendation in issues:
                writer.writerow([file_path, line_number, issue_type, description, recommendation])
        return output.getvalue()

    elif output_format == "json":
        formatted_results = []
        for file_path, issues in results.items():
            for line_number, issue_type, description, recommendation in issues:
                formatted_results.append({
                    "file": file_path,
                    "line_number": line_number,
                    "issue": issue_type,
                    "description": description,
                    "recommendation": recommendation
                })
        return json.dumps(formatted_results, indent=4)

    elif output_format == "html":
        output = io.StringIO()
        output.write("<html><head><title>Security Report</title></head><body>")
        output.write("<h1>Security Scan Report</h1><table border='1'><tr><th>File</th><th>Line Number</th><th>Issue</th><th>Description</th><th>Recommendation</th></tr>")
        for file_path, issues in results.items():
            for line_number, issue_type, description, recommendation in issues:
                output.write(f"<tr><td>{file_path}</td><td>{line_number}</td><td>{issue_type}</td><td>{description}</td><td>{recommendation}</td></tr>")
        output.write("</table></body></html>")
        return output.getvalue()

    elif output_format == "pdf":
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        styles = getSampleStyleSheet()
        paragraph_style = ParagraphStyle(name='Body', alignment=TA_LEFT, fontSize=8, spaceAfter=4)

        elements = [Paragraph("Security Scan Report", styles["Title"]), Spacer(1, 12)]

        data = [['File', 'Line Number', 'Issue', 'Description', 'Recommendation']]
        for file_path, issues in results.items():
            for line_number, issue_type, description, recommendation in issues:
                data.append([
                    Paragraph(file_path, paragraph_style),
                    str(line_number),
                    issue_type,
                    Paragraph(description, paragraph_style),
                    Paragraph(recommendation, paragraph_style)
                ])

        table = Table(data, repeatRows=1, colWidths=[100, 40, 70, 150, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#007BFF")),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
        ]))
        elements.append(table)
        doc.build(elements)
        return output.getvalue()

    return None

def scan_file(file_path, output_format="csv"):
    results = {}
    issues = []
    issues.extend(detect_sensitive_comments(file_path, delay=False))
    issues.extend(detect_hardcoded_secrets(file_path, delay=False))
    issues.extend(detect_insecure_error_messages(file_path, delay=False))

    if issues:
        results[file_path] = issues

    report_content = save_report(results, output_format) if results else None
    return results, report_content

def scan_directory(directory_path, output_format="csv"):
    extensions = ['.py', '.js', '.java', '.html', '.php', '.c', '.cpp', '.h', '.sh', '.yaml', '.yml', '.json']
    results = {}

    for file_path in traverse_directory(directory_path, extensions):
        issues = []
        issues.extend(detect_sensitive_comments(file_path, delay=True))
        issues.extend(detect_hardcoded_secrets(file_path, delay=True))
        issues.extend(detect_insecure_error_messages(file_path, delay=True))

        if issues:
            results[file_path] = issues

    report_content = save_report(results, output_format) if results else None
    return results, report_content
