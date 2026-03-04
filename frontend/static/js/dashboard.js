/**
 * CareerAI - Student Dashboard JS (dashboard.js)
 * =================================================
 * Handles all student dashboard interactions:
 * - Resume upload and skill extraction
 * - Skill gap analysis
 * - Learning roadmap generation
 * - AI Chatbot
 * - Analytics charts
 */

// ============ State ============
let userSkills = [];
let gapAnalysisResult = null;
let charts = {};

// ============ Init ============
document.addEventListener('DOMContentLoaded', async () => {
  if (!requireAuth('student')) return;
  
  const user = getUser();
  
  // Set user info
  document.getElementById('welcome-name').textContent = user.name.split(' ')[0];
  document.getElementById('sidebar-user-name').textContent = user.name;
  document.getElementById('user-avatar-text').textContent = user.name[0].toUpperCase();
  document.getElementById('topbar-greeting').textContent = `Hello, ${user.name.split(' ')[0]}!`;
  
  // Load career roles for dropdowns
  await loadCareerRoles();
  
  // Load user skills from profile
  await loadUserProfile();
  
  // Setup resume upload
  setupResumeUpload();
  
  // Show overview
  showSection('overview');
});

// ============ Section Navigation ============
function showSection(name) {
  // Hide all sections
  document.querySelectorAll('.dashboard-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(n => n.classList.remove('active'));
  
  // Show target
  const section = document.getElementById(`section-${name}`);
  if (section) section.classList.add('active');
  
  // Activate nav item
  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  navItems.forEach(item => {
    if (item.getAttribute('onclick')?.includes(name)) item.classList.add('active');
  });
  
  // Update topbar title
  const titles = {
    'overview': 'Overview',
    'resume': 'Resume & Skills',
    'gap-analysis': 'Skill Gap Analysis',
    'roadmap': 'Learning Roadmap',
    'jobs': 'Browse Jobs',
    'chatbot': 'AI Career Mentor',
    'analytics': 'Platform Analytics'
  };
  document.getElementById('page-title').textContent = titles[name] || name;
  
  // Lazy-load section content
  if (name === 'jobs') loadJobs();
  if (name === 'analytics') loadAnalytics();
  
  // Close mobile sidebar
  document.getElementById('sidebar')?.classList.remove('open');
}

// ============ Load Career Roles ============
async function loadCareerRoles() {
  try {
    const res = await apiRequest('/api/job-roles');
    if (!res.ok) return;
    const data = await res.json();
    
    // Populate both dropdowns
    const selectors = ['career-goal-select', 'modal-career-goal'];
    selectors.forEach(id => {
      const sel = document.getElementById(id);
      if (!sel) return;
      data.roles.forEach(role => {
        const opt = document.createElement('option');
        const roleName = typeof role === 'string' ? role : role.role_name;
        opt.value = roleName;
        opt.textContent = roleName;
        sel.appendChild(opt);
      });
    });
  } catch (e) {
    console.error('Failed to load career roles:', e);
  }
}

// ============ Load User Profile ============
async function loadUserProfile() {
  try {
    const res = await apiRequest('/api/student/profile');
    if (!res.ok) return;
    const data = await res.json();
    
    if (data.skills) {
      userSkills = data.skills;
      renderSkills(userSkills);
      updateOverviewStats();
    }
    
    if (data.career_goal) {
      const sel = document.getElementById('career-goal-select');
      if (sel) sel.value = data.career_goal;
    }
  } catch (e) {
    console.error('Profile load error:', e);
  }
}

// ============ Resume Upload ============
function setupResumeUpload() {
  const zone = document.getElementById('upload-zone');
  const fileInput = document.getElementById('resume-file');
  
  if (!zone || !fileInput) return;
  
  // Drag and drop
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) uploadResume(file);
  });
  
  fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) uploadResume(e.target.files[0]);
  });
}

async function uploadResume(file) {
  const progressDiv = document.getElementById('upload-progress');
  const resultDiv = document.getElementById('upload-result');
  const bar = document.getElementById('upload-bar');
  const pct = document.getElementById('upload-pct');
  
  progressDiv.classList.remove('d-none');
  resultDiv.innerHTML = '';
  
  // Animate progress bar
  let progress = 0;
  const interval = setInterval(() => {
    progress += 8;
    if (progress > 90) { clearInterval(interval); }
    bar.style.width = `${progress}%`;
    pct.textContent = `${progress}%`;
  }, 100);
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${window.API_BASE}/api/upload-resume`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` },
      body: formData
    });
    
    clearInterval(interval);
    bar.style.width = '100%';
    pct.textContent = '100%';
    
    const data = await res.json();
    
    if (res.ok) {
      // Update skills
      userSkills = [...new Set([...userSkills, ...(data.extracted_skills || [])])];
      renderSkills(userSkills);
      updateOverviewStats();
      
      resultDiv.innerHTML = `
        <div class="alert alert-success py-2 mb-0">
          <i class="bi bi-check-circle-fill me-2"></i>
          <strong>Resume processed!</strong> Found ${data.extracted_skills?.length || 0} skills.
        </div>`;
      showToast(`Resume uploaded! Found ${data.extracted_skills?.length || 0} skills.`, 'success');
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger py-2 mb-0"><i class="bi bi-x-circle-fill me-2"></i>${data.detail}</div>`;
    }
  } catch (e) {
    clearInterval(interval);
    resultDiv.innerHTML = `<div class="alert alert-danger py-2 mb-0">Upload failed. Check server connection.</div>`;
  } finally {
    setTimeout(() => progressDiv.classList.add('d-none'), 2000);
  }
}

// ============ Render Skills ============
function renderSkills(skills) {
  const container = document.getElementById('skills-container');
  if (!container) return;
  
  if (!skills || skills.length === 0) {
    container.innerHTML = `
      <div class="text-center text-muted py-4">
        <i class="bi bi-cpu fs-2 opacity-25"></i>
        <p class="mt-2 small">No skills yet. Upload a resume or add manually.</p>
      </div>`;
    return;
  }
  
  container.innerHTML = `
    <div class="skills-grid">
      ${skills.map(skill => `
        <div class="skill-badge">
          <i class="bi bi-check2 small"></i>
          ${skill}
          <span class="remove-btn" onclick="removeSkill('${skill}')">×</span>
        </div>
      `).join('')}
    </div>
    <div class="mt-3 text-muted small">
      <i class="bi bi-info-circle me-1"></i>
      ${skills.length} skill${skills.length !== 1 ? 's' : ''} detected
    </div>`;
}

function removeSkill(skill) {
  userSkills = userSkills.filter(s => s !== skill);
  renderSkills(userSkills);
  updateOverviewStats();
  saveSkillsToProfile();
}

async function saveSkillsToProfile() {
  try {
    await apiRequest('/api/student/profile', {
      method: 'PUT',
      body: JSON.stringify({ skills: userSkills })
    });
  } catch (e) {}
}

// ============ Manual Skill Add Modal ============
function openAddSkillModal() {
  // Pre-fill textarea if skills exist
  document.getElementById('manual-skills-input').value = userSkills.join(', ');
  new bootstrap.Modal(document.getElementById('addSkillModal')).show();
}

async function saveManualSkills() {
  const input = document.getElementById('manual-skills-input').value;
  const careerGoal = document.getElementById('modal-career-goal').value;
  
  const newSkills = input.split(',')
    .map(s => s.trim())
    .filter(s => s.length > 1);
  
  userSkills = [...new Set(newSkills)];
  renderSkills(userSkills);
  updateOverviewStats();
  
  try {
    await apiRequest('/api/student/profile', {
      method: 'PUT',
      body: JSON.stringify({ skills: userSkills, career_goal: careerGoal || undefined })
    });
    showToast('Skills saved successfully!', 'success');
  } catch (e) {
    showToast('Failed to save skills', 'error');
  }
  
  bootstrap.Modal.getInstance(document.getElementById('addSkillModal')).hide();
}

// ============ Skill Gap Analysis ============
async function runGapAnalysis() {
  const careerGoal = document.getElementById('career-goal-select').value;
  if (!careerGoal) {
    showToast('Please select a career goal first', 'warning');
    return;
  }
  
  if (userSkills.length === 0) {
    showToast('Please add some skills first (upload resume or add manually)', 'warning');
    return;
  }
  
  try {
    const res = await apiRequest('/api/skill-gap', {
      method: 'POST',
      body: JSON.stringify({ career_goal: careerGoal, skills: userSkills })
    });
    
    const data = await res.json();
    gapAnalysisResult = data;
    
    renderGapResults(data);
    updateOverviewStats();
    showToast('Gap analysis complete!', 'success');
    
  } catch (e) {
    showToast('Gap analysis failed. Try again.', 'error');
  }
}

function renderGapResults(data) {
  const resultsDiv = document.getElementById('gap-results');
  const placeholder = document.getElementById('gap-placeholder');
  
  resultsDiv.classList.remove('d-none');
  placeholder.classList.add('d-none');
  
  // Match percentage
  const pct = data.match_percentage;
  const circle = document.getElementById('match-circle');
  const display = document.getElementById('match-pct-display');
  const label = document.getElementById('match-career-label');
  
  display.textContent = `${pct}%`;
  label.textContent = `match for ${data.career_goal}`;
  
  // Color coding
  const color = pct >= 70 ? '#22c55e' : pct >= 40 ? '#f59e0b' : '#ef4444';
  circle.style.background = `conic-gradient(${color} ${pct}%, rgba(255,255,255,0.07) 0%)`;
  
  // Chart
  renderGapChart(data.matched_skills, data.missing_skills);
  
  // Matched skills
  const matchedList = document.getElementById('matched-skills-list');
  if (data.matched_skills.length > 0) {
    matchedList.innerHTML = data.matched_skills.map(s => `
      <div class="skill-list-item matched">
        <span><i class="bi bi-check-circle-fill me-2"></i>${s}</span>
        <span class="badge bg-success bg-opacity-25 text-success">✓ Have it</span>
      </div>`).join('');
  } else {
    matchedList.innerHTML = '<p class="text-muted small">No matching skills yet</p>';
  }
  
  // Missing skills
  const missingList = document.getElementById('missing-skills-list');
  if (data.missing_skills.length > 0) {
    missingList.innerHTML = data.missing_skills.map(s => `
      <div class="skill-list-item missing">
        <span><i class="bi bi-x-circle-fill me-2"></i>${s}</span>
        <span class="badge bg-danger bg-opacity-25 text-danger">Learn this</span>
      </div>`).join('');
  } else {
    missingList.innerHTML = '<p class="text-success small"><i class="bi bi-stars me-1"></i>You have all required skills! 🎉</p>';
  }
}

function renderGapChart(matched, missing) {
  const ctx = document.getElementById('gap-chart');
  if (!ctx) return;
  
  if (charts.gap) charts.gap.destroy();
  
  charts.gap = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [...matched.slice(0, 5), ...missing.slice(0, 5)],
      datasets: [{
        label: 'Skills',
        data: [...matched.slice(0, 5).map(() => 1), ...missing.slice(0, 5).map(() => 1)],
        backgroundColor: [
          ...matched.slice(0, 5).map(() => 'rgba(34,197,94,0.7)'),
          ...missing.slice(0, 5).map(() => 'rgba(239,68,68,0.7)')
        ],
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const idx = ctx.dataIndex;
              return idx < matched.length ? '✓ You have this skill' : '✗ Need to learn';
            }
          }
        }
      },
      scales: {
        x: { display: false },
        y: {
          ticks: { color: '#94a3b8', font: { size: 12 } },
          grid: { display: false }
        }
      }
    }
  });
}

async function generateRoadmapFromGap() {
  if (!gapAnalysisResult) {
    await runGapAnalysis();
    if (!gapAnalysisResult) return;
  }
  
  const missing = gapAnalysisResult.missing_skills;
  if (missing.length === 0) {
    showToast('You already have all required skills! No roadmap needed.', 'success');
    return;
  }
  
  try {
    const res = await apiRequest('/api/generate-roadmap', {
      method: 'POST',
      body: JSON.stringify({
        missing_skills: missing,
        career_goal: gapAnalysisResult.career_goal
      })
    });
    
    const data = await res.json();
    renderRoadmap(data);
    showSection('roadmap');
    
    // Update overview stat
    document.getElementById('stat-months').textContent = `${data.total_months}mo`;
    showToast('Roadmap generated! Check the Roadmap section.', 'success');
    
  } catch (e) {
    showToast('Roadmap generation failed', 'error');
  }
}

// ============ Render Roadmap ============
function renderRoadmap(data) {
  const container = document.getElementById('roadmap-container');
  
  const stepsHtml = data.roadmap.map((step, i) => `
    <div class="roadmap-item">
      <div class="roadmap-month-badge">Month ${step.month}</div>
      <h5>${step.phase || step.primary_skill || 'Learning Phase'}</h5>
      <p class="text-muted small mb-2">${step.description || step.learning || ''}</p>
      <div class="mb-2">
        ${(step.skills || []).map(s => `<span class="job-skill-tag me-1">${s}</span>`).join('')}
      </div>
      ${step.resources && step.resources.length > 0 ? `
        <div class="roadmap-resources">
          <small class="text-muted me-2">Resources:</small>
          ${step.resources.map(r => `
            <a href="${r.url}" target="_blank" class="resource-link">
              <i class="bi bi-link-45deg me-1"></i>${r.title || r.name}
            </a>`).join('')}
        </div>` : ''}
      ${step.projects && step.projects.length > 0 ? `
        <div class="mt-2">
          <small class="text-warning"><i class="bi bi-lightning me-1"></i>Project: ${step.projects[0]}</small>
        </div>` : ''}
    </div>
  `).join('');
  
  container.innerHTML = `
    <div class="content-card mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-1">Your Learning Roadmap</h5>
          <p class="text-muted small mb-0">
            Career Goal: <strong class="text-gradient">${data.career_goal || 'Custom'}</strong>
            &nbsp;•&nbsp; ${data.total_months} month${data.total_months !== 1 ? 's' : ''} plan
          </p>
        </div>
        <button class="btn btn-sm btn-outline-primary" onclick="generateRoadmapFromGap()">
          <i class="bi bi-arrow-clockwise me-1"></i>Regenerate
        </button>
      </div>
    </div>
    <div class="roadmap-timeline">
      ${stepsHtml}
    </div>`;
}

// ============ Update Overview Stats ============
function updateOverviewStats() {
  document.getElementById('stat-skills').textContent = userSkills.length;
  
  if (gapAnalysisResult) {
    document.getElementById('stat-missing').textContent = gapAnalysisResult.missing_skills.length;
    document.getElementById('stat-match').textContent = `${gapAnalysisResult.match_percentage}%`;
  }
}

// ============ Load Jobs ============
async function loadJobs() {
  const container = document.getElementById('jobs-list');
  if (!container) return;
  
  try {
    const res = await fetch(`${window.API_BASE}/api/jobs`);
    const data = await res.json();
    
    if (!data.jobs || data.jobs.length === 0) {
      container.innerHTML = `
        <div class="col-12 text-center py-5 text-muted">
          <i class="bi bi-briefcase fs-1 opacity-25"></i>
          <p class="mt-2">No job postings available yet.</p>
        </div>`;
      return;
    }
    
    container.innerHTML = data.jobs.map(job => `
      <div class="col-md-6">
        <div class="job-card">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
              <div class="job-title">${job.job_title}</div>
              <div class="job-meta">
                <i class="bi bi-person-badge me-1"></i>${job.recruiter_name || 'Company'}
                <span class="mx-2">•</span>
                <i class="bi bi-geo-alt me-1"></i>${job.location || 'Remote'}
                <span class="mx-2">•</span>
                <i class="bi bi-clock me-1"></i>${job.job_type || 'Full-time'}
              </div>
            </div>
            <span class="badge bg-primary bg-opacity-20 text-primary border border-primary border-opacity-25">
              ${job.required_skills?.length || 0} skills
            </span>
          </div>
          ${job.description ? `<p class="text-muted small mb-2">${job.description.slice(0, 100)}${job.description.length > 100 ? '...' : ''}</p>` : ''}
          <div class="job-skills">
            ${(job.required_skills || []).slice(0, 6).map(s => `<span class="job-skill-tag">${s}</span>`).join('')}
            ${job.required_skills?.length > 6 ? `<span class="job-skill-tag">+${job.required_skills.length - 6} more</span>` : ''}
          </div>
          <div class="mt-3">
            <small class="text-muted">${new Date(job.created_at).toLocaleDateString()}</small>
          </div>
        </div>
      </div>`).join('');
  } catch (e) {
    container.innerHTML = `
      <div class="col-12 text-center py-4 text-muted">
        <p>Failed to load jobs. Check connection.</p>
      </div>`;
  }
}

// ============ Chatbot ============
async function sendMessage() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;
  
  input.value = '';
  appendMessage(message, 'user');
  
  const typingEl = document.getElementById('typing-indicator');
  typingEl.classList.remove('d-none');
  
  try {
    const res = await apiRequest('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: 'main' })
    });
    
    const data = await res.json();
    typingEl.classList.add('d-none');
    appendMessage(data.reply, 'bot', data.sources);
    
  } catch (e) {
    typingEl.classList.add('d-none');
    appendMessage('Sorry, I had trouble responding. Please try again.', 'bot');
  }
}

function sendQuickMessage(message) {
  document.getElementById('chat-input').value = message;
  sendMessage();
}

function appendMessage(text, sender, sources = []) {
  const container = document.getElementById('chat-messages');
  const isBot = sender === 'bot';
  
  const div = document.createElement('div');
  div.className = `chat-message ${isBot ? 'bot-message' : 'user-message'}`;
  
  const sourcesHtml = sources && sources.length > 0 ? `
    <div class="message-sources">
      ${sources.map(s => `<a href="${s}" target="_blank" class="source-chip">${new URL(s).hostname}</a>`).join('')}
    </div>` : '';
  
  div.innerHTML = `
    <div class="message-avatar ${isBot ? 'bot-avatar' : 'user-avatar-chat'}">
      ${isBot ? '<i class="bi bi-robot"></i>' : '<i class="bi bi-person-fill"></i>'}
    </div>
    <div class="message-bubble">
      <p class="mb-0">${text.replace(/\n/g, '<br>')}</p>
      ${sourcesHtml}
    </div>`;
  
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

async function clearChat() {
  try {
    await apiRequest('/api/chat/history?session_id=main', { method: 'DELETE' });
  } catch (e) {}
  
  const container = document.getElementById('chat-messages');
  container.innerHTML = `
    <div class="chat-message bot-message">
      <div class="message-avatar bot-avatar"><i class="bi bi-robot"></i></div>
      <div class="message-bubble">
        <p class="mb-1">Chat cleared! How can I help you today?</p>
      </div>
    </div>`;
}

// ============ Analytics Charts ============
async function loadAnalytics() {
  try {
    const token = getToken();
    const headers = { 'Authorization': `Bearer ${token}` };
    
    // Parallel API calls
    const [skillsRes, careerRes, matchRes, overviewRes] = await Promise.all([
      fetch(`${window.API_BASE}/api/analytics/top-skills`, { headers }),
      fetch(`${window.API_BASE}/api/analytics/career-distribution`, { headers }),
      fetch(`${window.API_BASE}/api/analytics/match-scores`, { headers }),
      fetch(`${window.API_BASE}/api/analytics/overview`, { headers })
    ]);
    
    const [skillsData, careerData, matchData, overviewData] = await Promise.all([
      skillsRes.json(), careerRes.json(), matchRes.json(), overviewRes.json()
    ]);
    
    // Top Skills Bar Chart
    renderBarChart('skills-chart', skillsData.labels, skillsData.data, 'Demand Count',
      'rgba(99,102,241,0.8)', '#0b1120');
    
    // Career Doughnut Chart
    renderDoughnutChart('career-chart', careerData.labels, careerData.data);
    
    // Match Score Bar Chart
    renderBarChart('match-chart', matchData.labels, matchData.data, 'Candidates',
      'rgba(34,197,94,0.8)', '#0b1120');
    
    // Overview stats
    document.getElementById('total-students').textContent = overviewData.total_students;
    document.getElementById('total-jobs').textContent = overviewData.total_jobs;
    document.getElementById('total-recruiters').textContent = overviewData.total_recruiters;
    document.getElementById('total-roadmaps').textContent = overviewData.total_roadmaps;
    
  } catch (e) {
    console.error('Analytics load failed:', e);
  }
}

function renderBarChart(canvasId, labels, data, label, color, bg) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();
  
  charts[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label, data, backgroundColor: color, borderRadius: 6, borderSkipped: false }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#64748b', font: { size: 11 } }, grid: { display: false } },
        y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.04)' } }
      }
    }
  });
}

function renderDoughnutChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (charts[canvasId]) charts[canvasId].destroy();
  
  const colors = ['#6366f1','#22c55e','#f59e0b','#ef4444','#0ea5e9','#a78bfa','#34d399'];
  
  charts[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderWidth: 2, borderColor: '#0b1120' }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: { color: '#94a3b8', font: { size: 11 }, boxWidth: 12, padding: 12 }
        }
      }
    }
  });
}
