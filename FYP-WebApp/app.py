from flask import Flask, render_template, request, jsonify, send_file
import os
import zipfile
import io
from scanner import scan_file, scan_directory

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    scan_type = request.form.get("scan_type")
    output_format = request.form.get("output_format", "csv")

    if scan_type == "file":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        file_name = os.path.splitext(uploaded_file.filename)[0]
        file_path = os.path.join("uploads", uploaded_file.filename)
        uploaded_file.save(file_path)

        results, report_content = scan_file(file_path, output_format)
        os.remove(file_path)

        if report_content:
            if output_format == "pdf":
                return send_file(
                    io.BytesIO(report_content),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=f"{file_name}_report.pdf"
                )
            return send_file(
                io.BytesIO(report_content.encode()),
                mimetype="text/csv" if output_format == "csv" else
                         "application/json" if output_format == "json" else
                         "text/html",
                as_attachment=True,
                download_name=f"{file_name}_report.{output_format}"
            )
        return jsonify({"error": "No issues found."})

    elif scan_type == "directory":
        if "directory_zip" not in request.files:
            return jsonify({"error": "No ZIP file uploaded"}), 400

        uploaded_zip = request.files["directory_zip"]
        if uploaded_zip.filename == "":
            return jsonify({"error": "No selected ZIP file"}), 400

        zip_name = os.path.splitext(uploaded_zip.filename)[0]
        zip_path = os.path.join("uploads", uploaded_zip.filename)
        uploaded_zip.save(zip_path)
        extract_path = os.path.join("uploads", "extracted")
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        results, report_content = scan_directory(extract_path, output_format)

        # Cleanup
        for root, dirs, files in os.walk(extract_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(extract_path)
        os.remove(zip_path)

        if report_content:
            if output_format == "pdf":
                return send_file(
                    io.BytesIO(report_content),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=f"{zip_name}_report.pdf"
                )
            return send_file(
                io.BytesIO(report_content.encode()),
                mimetype="text/csv" if output_format == "csv" else
                         "application/json" if output_format == "json" else
                         "text/html",
                as_attachment=True,
                download_name=f"{zip_name}_report.{output_format}"
            )
        return jsonify({"error": "No issues found."})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
