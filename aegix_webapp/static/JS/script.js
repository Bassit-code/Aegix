// Toggles between file and directory input fields based on scan type selection
function toggleInputType() {
  const scanType = document.getElementById("scan_type").value;
  // Show file input if 'file' is selected, otherwise hide it
  document.getElementById("file_input").style.display =
    scanType === "file" ? "block" : "none";
  // Show directory input if 'directory' is selected, otherwise hide it
  document.getElementById("dir_input").style.display =
    scanType === "directory" ? "block" : "none";
}

// Handles the scan button click: uploads the file/dir, shows overlay, and manages download link
function scanCode() {
  // Show the scanning overlay
  document.getElementById("scannerOverlay").style.display = "block";
  // Hide and reset the download link
  document.getElementById("download_link").classList.remove("show-download");
  document.getElementById("download_link").style.display = "none";

  // Gather form data for upload
  const formData = new FormData(document.getElementById("scanForm"));
  // Send the form data to the server for scanning
  fetch("/scan", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      // If upload fails, show an error
      if (!response.ok)
        throw new Error(
          "Upload required! Please choose a file or ZIP file before scanning"
        );
      // Otherwise, get the response as a blob (the report)
      return response.blob();
    })
    .then((blob) => {
      // Generate a timestamp for the report filename
      const now = new Date();
      const timestamp =
        [
          now.getFullYear(),
          String(now.getMonth() + 1).padStart(2, "0"),
          String(now.getDate()).padStart(2, "0"),
        ].join("") +
        "T" +
        [
          String(now.getHours()).padStart(2, "0"),
          String(now.getMinutes()).padStart(2, "0"),
          String(now.getSeconds()).padStart(2, "0"),
        ].join("");

      // Get the selected output format (e.g., pdf, txt)
      const selectedFormat = document.getElementById("output_format").value;
      // Create a URL for the downloaded report
      const url = window.URL.createObjectURL(blob);
      const downloadLink = document.getElementById("download_link");

      // Set up the download link with filename and URL
      downloadLink.href = url;
      downloadLink.download = `security_report_${timestamp}.${selectedFormat}`;
      downloadLink.style.display = "inline-block";
      downloadLink.classList.add("show-download");

      // Play a sound to indicate scan completion, if available
      const sound = document.getElementById("dingSound");
      if (sound) {
        sound
          .play()
          .catch((err) => console.warn("Sound failed to play:", err));
      }

      // Hide the scanning overlay
      document.getElementById("scannerOverlay").style.display = "none";
    })
    .catch((error) => {
      // Show error message and hide overlay if scan fails
      alert(error.message);
      document.getElementById("scannerOverlay").style.display = "none";
    });
}

// Theme preference logic

// Get the theme toggle switch element
const themeToggle = document.querySelector(".theme-switch input");
// Get user's saved theme preference from localStorage
const userPreference = localStorage.getItem("theme");
// Detect system theme preference (dark or light)
const systemPreference = window.matchMedia("(prefers-color-scheme: dark)").matches
  ? "dark"
  : "light";

// Apply user or system theme preference on page load
if (userPreference) {
  document.documentElement.classList.toggle("dark", userPreference === "dark");
  themeToggle.checked = userPreference === "dark";
} else {
  document.documentElement.classList.toggle("dark", systemPreference === "dark");
  themeToggle.checked = systemPreference === "dark";
}

// Listen for theme toggle switch changes and update theme accordingly
themeToggle.addEventListener("click", () => {
  if (themeToggle.checked) {
    document.documentElement.classList.add("dark");
    localStorage.setItem("theme", "dark");
  } else {
    document.documentElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
  }
});