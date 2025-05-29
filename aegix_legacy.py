# Original version: 1.0 (Outdated)

import os
import re
import csv
from datetime import datetime

def traverse_directory(directory_path, file_extensions):
    """Recursively traverse the directory and yield files with specified extensions."""
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(tuple(file_extensions)):
                yield os.path.join(root, file)

def detect_sensitive_comments(file_path):
    """Detect comments in the file that might contain sensitive information."""
    comment_keywords = ['TODO', 'FIXME', 'password', 'secret', 'key']
    sensitive_comments = []
    comment_pattern = re.compile(r'#.*|//.*|/\*.*?\*/', re.DOTALL)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if comment_pattern.search(line):
                for keyword in comment_keywords:
                    if keyword.lower() in line.lower():
                        sensitive_comments.append((line_number, line.strip()))
                        break
    return sensitive_comments

def detect_hardcoded_secrets(file_path):
    """Detect hardcoded secrets like passwords and API keys."""
    secret_pattern = re.compile(r'(password|pwd|api_key|access_token|secret|key)\s*=\s*[\'\"].+[\'\"]', re.IGNORECASE)
    hardcoded_secrets = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if secret_pattern.search(line):
                hardcoded_secrets.append((line_number, line.strip()))
    return hardcoded_secrets

def detect_insecure_error_messages(file_path):
    """Detect error messages that may leak sensitive information."""
    error_keywords = ['print', 'log', 'raise', 'traceback']
    insecure_errors = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line_number, line in enumerate(file, start=1):
            if any(keyword in line.lower() for keyword in error_keywords):
                insecure_errors.append((line_number, line.strip()))
    return insecure_errors

def save_report(results):
    """Save the results to a uniquely named CSV file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Create a unique timestamp
    output_file = f'security_report_{timestamp}.csv'  # Generate file name with timestamp

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File', 'Line Number', 'Issue', 'Description'])
        for file_path, issues in results.items():
            for line_number, issue_type, description in issues:
                writer.writerow([file_path, line_number, issue_type, description])
    print(f"\nReport saved as {output_file}")

def get_user_input():
    """Prompt the user to choose between scanning a file or a directory with proper validation."""
    print("Choose an option:")
    print("1. Scan a specific file")
    print("2. Scan a directory")
    
    while True:
        choice = input("Enter 1 or 2: ")
        if choice == '1':
            while True:
                file_path = input("Enter the file path to scan: ")
                if os.path.isfile(file_path):
                    return 'file', file_path
                else:
                    print("Invalid file path. Please enter a valid file path.")
        elif choice == '2':
            while True:
                directory_path = input("Enter the directory path to scan: ")
                if os.path.isdir(directory_path):
                    return 'directory', directory_path
                else:
                    print("Invalid directory path. Please enter a valid directory path.")
        else:
            print("Invalid input. Please enter 1 or 2.")

if __name__ == "__main__":
    # Input from the user
    scan_type, path = get_user_input()
    extensions = ['.py', '.js', '.java', '.html', '.php', '.c', '.cpp', '.h', '.sh', '.yaml', '.yml', '.json']
    
    print("\nScanning for issues...\n")
    results = {}

    if scan_type == 'file':
        files_to_scan = [path]
    else:
        files_to_scan = traverse_directory(path, extensions)
    
    for file in files_to_scan:
        issues = []
        issues.extend([(ln, 'Sensitive Comment', desc) for ln, desc in detect_sensitive_comments(file)])
        issues.extend([(ln, 'Hardcoded Secret', desc) for ln, desc in detect_hardcoded_secrets(file)])
        issues.extend([(ln, 'Insecure Error Message', desc) for ln, desc in detect_insecure_error_messages(file)])
        
        if issues:
            results[file] = issues
            print(f"File: {file}")
            for line_number, issue_type, description in issues:
                print(f"  Line {line_number}: [{issue_type}] {description}")
            print()
    
    # Save the results to a CSV file
    if results:
        save_report(results)
    else:
        print("No issues found.")
