import os
import re
import csv
import json
import io

def traverse_directory(directory_path, file_extensions):
    """Recursively traverse a directory and yield files with specific extensions."""
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(tuple(file_extensions)):
                yield os.path.join(root, file)

def detect_sensitive_comments(file_path):
    """Detect comments in various file types, including JSON."""
    comment_keywords = ['TODO', 'FIXME', 'password', 'secret', 'key']
    sensitive_comments = []

    # Regular expressions for different comment styles
    comment_patterns = [
        re.compile(r'#.*'),  # Python-style comments (#)
        re.compile(r'//.*'),  # C, C++, Java, JavaScript-style comments (//)
        re.compile(r'/\*.*?\*/', re.DOTALL),  # Multi-line block comments (/* ... */)
        re.compile(r'<!--(.*?)-->', re.DOTALL)  # HTML-style comments (<!-- ... -->)
    ]

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    # Check for standard comment patterns
    for line_number, line in enumerate(lines, start=1):
        for pattern in comment_patterns:
            matches = pattern.findall(line)
            for match in matches:
                if any(keyword.lower() in match.lower() for keyword in comment_keywords):
                    sensitive_comments.append((line_number, "Sensitive Comment", match.strip()))

    # JSON-Specific Comment Detection (Keys like '__comment' or '_note')
    if file_path.endswith(".json"):
        try:
            import json
            json_data = json.loads(''.join(lines))  # Parse JSON
            for key, value in json_data.items():
                if isinstance(value, str):  # Check if value is a string (potential comment)
                    if key.lower() in ["__comment", "_note", "comment"]:
                        if any(keyword.lower() in value.lower() for keyword in comment_keywords):
                            sensitive_comments.append((1, "Sensitive Comment", f"{key}: {value.strip()}"))
        except json.JSONDecodeError:
            pass  # Ignore if it's not valid JSON (prevents breaking)

    return sensitive_comments



def detect_hardcoded_secrets(file_path):
    """Detect hardcoded secrets such as passwords and API keys."""
    secret_pattern = re.compile(r'(password|pwd|api_key|access_token|secret|key)\s*=\s*[\'\"].+[\'\"]', re.IGNORECASE)
    hardcoded_secrets = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if secret_pattern.search(line):
                hardcoded_secrets.append((line_number, "Hardcoded Secret", line.strip()))
    return hardcoded_secrets

def detect_insecure_error_messages(file_path):
    """Detect error messages that might expose sensitive information."""
    error_keywords = ['print', 'log', 'raise', 'traceback']
    insecure_errors = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if any(keyword in line.lower() for keyword in error_keywords):
                insecure_errors.append((line_number, "Insecure Error Message", line.strip()))
    return insecure_errors

def save_report(results, output_format):
    """Generate report in-memory instead of saving it on disk."""
    if output_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['File', 'Line Number', 'Issue', 'Description'])
        for file_path, issues in results.items():
            for line_number, issue_type, description in issues:
                writer.writerow([file_path, line_number, issue_type, description])
        return output.getvalue()

    elif output_format == "json":
        return json.dumps(results, indent=4)

    elif output_format == "html":
        output = io.StringIO()
        output.write("<html><head><title>Security Report</title></head><body>")
        output.write("<h1>Security Scan Report</h1><table border='1'><tr><th>File</th><th>Line Number</th><th>Issue</th><th>Description</th></tr>")
        for file_path, issues in results.items():
            for line_number, issue_type, description in issues:
                output.write(f"<tr><td>{file_path}</td><td>{line_number}</td><td>{issue_type}</td><td>{description}</td></tr>")
        output.write("</table></body></html>")
        return output.getvalue()

    return None


def scan_file(file_path, output_format="csv"):
    """Scan a single file for security issues and generate an in-memory report."""
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
    """Scan an entire directory for security issues and generate an in-memory report."""
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
