from flask import Flask, request, jsonify, render_template_string
from classifier import TicketClassifier
import json

app = Flask(__name__)
classifier = TicketClassifier()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>VibeFI Ticket Intelligence Console</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://kit.fontawesome.com/a2d9d6fda1.js" crossorigin="anonymous"></script>
</head>
<body class="bg-gradient-to-br from-slate-100 via-white to-slate-200 min-h-screen font-inter flex items-center justify-center">

<div class="max-w-5xl w-full bg-white shadow-2xl rounded-3xl p-10">
  <div class="flex flex-col items-center text-center mb-8">
    <div class="flex items-center gap-3 mb-3">
      <div class="bg-blue-600 text-white p-3 rounded-xl shadow-md"><i class="fa-solid fa-robot text-lg"></i></div>
      <h1 class="text-3xl font-bold text-gray-800 tracking-tight">VibeFI Multi-Ticket AI Classifier</h1>
    </div>
    <p class="text-gray-600 text-sm max-w-xl">Upload or paste ticket JSON data below. The AI will determine whether each ticket requires an AI-generated patch or a Vibe-coded workflow.</p>
  </div>

  <!-- Input Controls -->
  <div class="bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-6 mb-6 shadow-inner">
    <div class="flex flex-col md:flex-row gap-3 mb-4">
      <select id="sampleSelect" onchange="loadSample()" 
        class="flex-1 border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 p-2 text-gray-700">
        <option value="">🔽 Choose Sample Dataset</option>
        <option value="basic">Basic Example</option>
        <option value="crash_mix">Crash + Login Mix</option>
      </select>

      <input type="file" id="fileInput" accept=".json"
        class="flex-1 border border-gray-300 rounded-lg p-2 text-gray-600 cursor-pointer bg-white hover:bg-gray-50 focus:ring-2 focus:ring-blue-500" 
        onchange="handleFileUpload(event)">
    </div>

    <textarea id="ticketInput" rows="7" placeholder='{"tickets": [{"channel": "Email", "severity": "High", "summary": "..."}, ...]}'
      class="w-full border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 p-4 font-mono text-sm text-gray-800 bg-white resize-none"></textarea>
  </div>

  <!-- Action Button -->
  <button onclick="classifyTickets()" 
    class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl shadow-lg transition duration-200 flex items-center justify-center gap-2">
    <i class="fa-solid fa-paper-plane"></i> Run Classification
  </button>

  <!-- Results -->
  <div id="resultsSection" class="hidden mt-10 animate-fade-in">
    <h2 class="text-2xl font-semibold text-gray-800 mb-5 flex items-center gap-2">
      <i class="fa-solid fa-chart-pie text-blue-600"></i> Classification Results
    </h2>

    <div class="overflow-x-auto rounded-2xl shadow-md border border-gray-200">
      <table class="min-w-full text-sm text-left border-collapse">
        <thead class="bg-gray-100 text-gray-700 font-semibold">
          <tr>
            <th class="p-3">#</th>
            <th class="p-3">Channel</th>
            <th class="p-3">Severity</th>
            <th class="p-3">Decision</th>
            <th class="p-3 w-[30%]">Reasoning</th>
            <th class="p-3">Next Actions</th>
          </tr>
        </thead>
        <tbody id="resultsTable" class="divide-y divide-gray-200 bg-white"></tbody>
      </table>
    </div>
  </div>
</div>

<style>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fade-in 0.5s ease-out; }
</style>

<script>
// --- Predefined Samples ---
const samples = {
  "basic": {
    "tickets": [
      {"channel":"Email","severity":"High","summary":"App crash on fund transfer after update"},
      {"channel":"Chat","severity":"Medium","summary":"Unable to reset login PIN"},
      {"channel":"Phone","severity":"Low","summary":"User asking how to enable biometric login"}
    ]
  },
  "crash_mix": {
    "tickets": [
      {"channel":"App","severity":"High","summary":"Crash when user uploads ID proof"},
      {"channel":"Chat","severity":"Low","summary":"How to activate netbanking?"},
      {"channel":"Email","severity":"Medium","summary":"Timeout error in API when checking balance"}
    ]
  }
};

// Load sample into textarea
function loadSample() {
  const selected = document.getElementById('sampleSelect').value;
  if (selected && samples[selected]) {
    document.getElementById('ticketInput').value = JSON.stringify(samples[selected], null, 2);
  }
}

// Handle file upload (.json)
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => document.getElementById('ticketInput').value = e.target.result;
  reader.readAsText(file);
}

// Submit JSON for classification
async function classifyTickets() {
  const text = document.getElementById('ticketInput').value.trim();
  if (!text) { alert("Please upload or paste ticket JSON first!"); return; }

  try {
    const data = JSON.parse(text);
    const res = await fetch('/classify_batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const results = await res.json();
    renderResults(results);
  } catch {
    alert("Invalid JSON format. Please ensure it’s valid JSON.");
  }
}

// Render Results Table
function renderResults(results) {
  const table = document.getElementById('resultsTable');
  table.innerHTML = "";
  results.forEach((r, idx) => {
    const decisionColor = r.decision === "AI_CODE_PATCH" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800";
    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="p-3 font-medium text-gray-700">${idx + 1}</td>
      <td class="p-3">${r.metadata.channel.toUpperCase()}</td>
      <td class="p-3">${r.metadata.severity.toUpperCase()}</td>
      <td class="p-3"><span class="px-2 py-1 rounded-md text-xs font-semibold ${decisionColor}">
        ${r.decision.replace("_", " ")}
      </span></td>
      <td class="p-3 text-gray-700 align-top">
        <div class="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 text-sm leading-snug whitespace-pre-wrap hover:bg-gray-100 transition duration-200">
          ${r.reasoning}
        </div>
      </td>
      <td class="p-3 text-gray-600">
        <details class="cursor-pointer">
          <summary class="text-blue-600 hover:underline text-sm">View Actions</summary>
          <ul class="list-disc list-inside text-gray-700 mt-1 text-sm space-y-1">
            ${r.next_actions.map(a => `<li>${a}</li>`).join('')}
          </ul>
        </details>
      </td>
    `;
    table.appendChild(row);
  });
  document.getElementById('resultsSection').classList.remove('hidden');
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
  return render_template_string(HTML_TEMPLATE)

@app.route('/classify_batch', methods=['POST'])
def classify_batch():
  data = request.json
  tickets = data.get("tickets", [])
  results = [classifier.classify(ticket) for ticket in tickets]
  return jsonify(results)

if __name__ == "__main__":
  app.run(debug=True)
