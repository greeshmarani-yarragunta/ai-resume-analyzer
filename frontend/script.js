const uploadForm = document.getElementById('uploadForm');
const status = document.getElementById('status');
const resultsDiv = document.getElementById('results');

function showStatus(msg){ status.classList.remove('hidden'); status.textContent = msg; }
function hideStatus(){ status.classList.add('hidden'); status.textContent=''; }

uploadForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fileInput = document.getElementById('resume');
  if(!fileInput.files.length) return alert('Choose a resume file');
  const formData = new FormData();
  formData.append('resume', fileInput.files[0]);

  showStatus('Uploading and analyzing... This may take a few seconds.');
  resultsDiv.classList.add('hidden');
  resultsDiv.innerHTML = '';

  try{
    const res = await fetch('/api/upload-resume', { method: 'POST', body: formData });
    const data = await res.json();
    if(!res.ok) throw new Error(data.error || 'Analysis failed');
    renderResults(data);
    hideStatus();
  }catch(err){
    showStatus('Error: ' + err.message);
  }
});

function renderResults(data){
  resultsDiv.classList.remove('hidden');
  const html = `
    <h2>Analysis: ${data.filename}</h2>
    <p><strong>Resume score:</strong> ${data.resume_score}/100</p>
    <p><strong>Top matches:</strong></p>
    <ul>
      ${Object.entries(data.match_scores).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([r,s])=>`<li>${r}: ${s}%</li>`).join('')}
    </ul>
    <p><strong>Skills detected:</strong> ${data.skills.join(', ') || 'None'}</p>
    <p><strong>Missing skills (for top role):</strong> ${data.missing_skills.join(', ') || 'None'}</p>
    <p><strong>Suggestions:</strong> ${data.suggestions}</p>
    <p><a href="/api/results/${data.resume_id}" target="_blank">View stored result (JSON)</a></p>
  `;
  resultsDiv.innerHTML = html + `
    <h3 style="margin-top: 30px;">Job Match Visualization</h3>
    <canvas id="matchChart" style="max-width: 600px; margin-top: 10px;"></canvas>
    `;

  renderCharts(data.match_scores);

}
function renderCharts(matchScores, skills, skillStrengths) {
  // destroy old charts safely
  if (window.matchChart && typeof window.matchChart.destroy === 'function') {
    window.matchChart.destroy();
  }
  if (window.skillChart && typeof window.skillChart.destroy === 'function') {
    window.skillChart.destroy();
  }


  // Job Match Bar Chart
  const ctx1 = document.getElementById('matchChart');
  window.matchChart = new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: Object.keys(matchScores),
      datasets: [{
        label: 'Match %',
        data: Object.values(matchScores),
        borderWidth: 1
      }]
    },
    options: {
      scales: { y: { beginAtZero: true, max: 100 } }
    }
  });

}

