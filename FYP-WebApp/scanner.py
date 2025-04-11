import os
import re
import csv
import json
import io

# Static security recommendations for each issue type
RECOMMENDATIONS = {
    "Sensitive Comment": "Remove any comments containing sensitive info before deploying.",
    "Hardcoded Secret": "Avoid hardcoding secrets. Use environment variables or secret managers.",
    "Insecure Error Message": "Avoid printing raw errors. Use logging libraries with proper levels."
}

def traverse_directory(directory_path, file_extensions):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(tuple(file_extensions)):
                yield os.path.join(root, file)

def detect_sensitive_comments(file_path):
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
                    sensitive_comments.append((line_number, "Sensitive Comment", match.strip(), RECOMMENDATIONS["Sensitive Comment"]))

    if file_path.endswith(".json"):
        try:
            json_data = json.loads(''.join(lines))
            for key, value in json_data.items():
                if isinstance(value, str):
                    if key.lower() in ["__comment", "_note", "comment"]:
                        if any(keyword.lower() in value.lower() for keyword in comment_keywords):
                            sensitive_comments.append((1, "Sensitive Comment", f"{key}: {value.strip()}", RECOMMENDATIONS["Sensitive Comment"]))
        except json.JSONDecodeError:
            pass

    return sensitive_comments

def detect_hardcoded_secrets(file_path):
    secret_pattern = re.compile(r'(password|pwd|api_key|access_token|secret|key|token|github_token|auth_token|client_secret)\s*=\s*[\'\"].+[\'\"]', re.IGNORECASE)
    hardcoded_secrets = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if secret_pattern.search(line):
                hardcoded_secrets.append((line_number, "Hardcoded Secret", line.strip(), RECOMMENDATIONS["Hardcoded Secret"]))
    return hardcoded_secrets

def detect_insecure_error_messages(file_path):
    error_keywords = ['print', 'log', 'raise', 'traceback']
    insecure_errors = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if any(keyword in line.lower() for keyword in error_keywords):
                insecure_errors.append((line_number, "Insecure Error Message", line.strip(), RECOMMENDATIONS["Insecure Error Message"]))
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

    return None

def scan_file(file_path, output_format="csv"):
    results = {}
    issues = []
    issues.extend(detect_sensitive_comments(file_path))
    issues.extend(detect_hardcoded_secrets(file_path))
    issues.extend(detect_insecure_error_messages(file_path))

    if issues:
        results[file_path] = issues

    report_content = save_report(results, output_format) if results else None
    return results, report_content

def scan_directory(directory_path, output_format="csv"):
    extensions = ['.py', '.js', '.java', '.html', '.php', '.c', '.cpp', '.h', '.sh', '.yaml', '.yml', '.json']
    results = {}

    for file_path in traverse_directory(directory_path, extensions):
        issues = []
        issues.extend(detect_sensitive_comments(file_path))
        issues.extend(detect_hardcoded_secrets(file_path))
        issues.extend(detect_insecure_error_messages(file_path))

        if issues:
            results[file_path] = issues

    report_content = save_report(results, output_format) if results else None
    return results, report_content
