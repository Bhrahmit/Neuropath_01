// ================================
// Skill Tag System
// ================================

function addSkillTag() {

  const input = document.getElementById("skill-input");
  const container = document.getElementById("required-skills-tags");

  if (!input || !container) return;

  const skill = input.value.trim();

  if (!skill) return;

  createSkillTag(skill);

  input.value = "";

}

function addSkill(skill) {

  createSkillTag(skill);

}

function createSkillTag(skill) {

  const container = document.getElementById("required-skills-tags");

  // prevent duplicates
  const existing = Array.from(container.children).find(
    tag => tag.innerText.replace("×","").trim().toLowerCase() === skill.toLowerCase()
  );

  if (existing) return;

  const tag = document.createElement("span");

  tag.className = "badge bg-primary me-1 skill-tag";

  tag.innerHTML = `
    ${skill}
    <span style="cursor:pointer;margin-left:5px;" onclick="this.parentElement.remove()">×</span>
  `;

  container.appendChild(tag);

}// ===============================
// Recruiter Dashboard Script
// ===============================


// -------------------------------
// Section Navigation
// -------------------------------
function showSection(section) {

  document.querySelectorAll(".dashboard-section").forEach(sec => {
    sec.classList.remove("active");
  });

  const target = document.getElementById("section-" + section);

  if (target) {
    target.classList.add("active");
  }

  document.getElementById("page-title").innerText =
    section.replace("-", " ").toUpperCase();
}


// -------------------------------
// Sidebar Toggle
// -------------------------------
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}


// -------------------------------
// Logout
// -------------------------------
function logout() {
  localStorage.removeItem("careerai_token");
  localStorage.removeItem("careerai_user");
  window.location.href = "/login";
}


// -------------------------------
// Load Recruiter Jobs
// -------------------------------
async function loadMyJobs() {

  try {

    const res = await apiRequest("/api/jobs/my");
    const data = await res.json();

    const container = document.getElementById("my-jobs-list");

    if (!data.jobs || data.jobs.length === 0) {

      container.innerHTML = `
      <div class="text-center text-muted py-5">
        No jobs posted yet
      </div>
      `;

      return;
    }

    container.innerHTML = "";

    data.jobs.forEach(job => {

      const card = document.createElement("div");

      card.className = "content-card mb-3";

      card.innerHTML = `
        <h5>${job.job_title}</h5>
        <p class="text-muted">${job.description || ""}</p>
        <small><b>Skills:</b> ${(job.required_skills || []).join(", ")}</small>
      `;

      container.appendChild(card);

    });

    populateMatchJobDropdown(data.jobs);

  } catch (err) {

    console.error("Error loading jobs:", err);

  }

}


// -------------------------------
// Populate Match Dropdown
// -------------------------------
function populateMatchJobDropdown(jobs) {

  const select = document.getElementById("match-job-select");

  if (!select) return;

  select.innerHTML = '<option value="">-- Select a job posting --</option>';

  jobs.forEach(job => {

    const option = document.createElement("option");

    option.value = job.id;
    option.textContent = job.job_title;

    select.appendChild(option);

  });

}


// -------------------------------
// Post Job
// -------------------------------
document.addEventListener("DOMContentLoaded", () => {

  loadMyJobs();

  const form = document.getElementById("post-job-form");

  if (!form) return;

  form.addEventListener("submit", async (e) => {

    e.preventDefault();

    const jobTitle = document.getElementById("job-title").value;
    const description = document.getElementById("job-description").value;

    const skills = [];

    document.querySelectorAll("#required-skills-tags .skill-tag").forEach(tag => {
      skills.push(tag.innerText.trim());
    });

    const payload = {
      job_title: jobTitle,
      description: description,
      required_skills: skills
    };

    try {

      const res = await apiRequest("/api/job-post", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      alert(data.message || "Job posted successfully");

      form.reset();

      loadMyJobs();

    } catch (err) {

      console.error("Post job error:", err);
      alert("Failed to post job");

    }

  });

});


// -------------------------------
// Run Candidate Matching
// -------------------------------
async function runCandidateMatching() {

  const jobId = document.getElementById("match-job-select").value;

  if (!jobId) {
    alert("Please select a job first");
    return;
  }

  try {

    const res = await apiRequest("/api/match-candidates", {
      method: "POST",
      body: JSON.stringify({ job_id: parseInt(jobId) })
    });

    const data = await res.json();

    displayCandidates(data.candidates || []);

  } catch (err) {

    console.error("Matching error:", err);
    alert("Matching failed");

  }

}


// -------------------------------
// Display Matched Candidates
// -------------------------------
function displayCandidates(candidates) {

  const container = document.getElementById("candidates-list");
  const resultBox = document.getElementById("candidates-result");

  if (!container) return;

  resultBox.classList.remove("d-none");

  if (candidates.length === 0) {

    container.innerHTML = `
      <div class="text-center text-muted py-4">
        No candidates found
      </div>
    `;

    return;
  }

  container.innerHTML = "";

  candidates.forEach(c => {

    const div = document.createElement("div");

    div.className = "content-card mb-2";

    div.innerHTML = `
      <div class="d-flex justify-content-between">
        <div>
          <h6>${c.name}</h6>
          <small class="text-muted">${c.email}</small>
        </div>
        <div>
          <span class="badge bg-success">${c.match_score}%</span>
        </div>
      </div>
    `;

    container.appendChild(div);

  });

  document.getElementById("candidates-count").innerText =
    candidates.length + " found";

}

function resetJobForm() {

  const form = document.getElementById("post-job-form");

  if (form) {
    form.reset();
  }

  const skillsContainer = document.getElementById("required-skills-tags");

  if (skillsContainer) {
    skillsContainer.innerHTML = "";
  }

}