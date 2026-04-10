// ── Tab navigation ──────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});


// ── Status helpers ──────────────────────────────────────────────────────────

function showStatus(id, type, msg, spinner = false) {
  const el = document.getElementById(id);
  el.className = `status-bar show ${type}`;
  el.innerHTML = (spinner ? '<div class="spinner"></div>' : '') + `<span>${msg}</span>`;
}

function clearStatus(id) {
  const el = document.getElementById(id);
  el.className = 'status-bar';
  el.innerHTML = '';
}


// ── API helpers ──────────────────────────────────────────────────────────────

async function api(method, path, body) {
  const opts = {
    method,
    headers: body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    body: body instanceof FormData ? body : (body ? JSON.stringify(body) : undefined),
  };
  const res = await fetch('/api' + path, opts);
  const data = await res.json().catch(() => ({ detail: res.statusText }));
  if (!res.ok) throw new Error(data.detail || 'Request failed');
  return data;
}


// ── Org data ─────────────────────────────────────────────────────────────────

let programs = [];
let stats = [];

async function loadOrgData() {
  try {
    const data = await api('GET', '/memory');
    const p = data.profile || {};
    document.getElementById('mission').value          = p.mission || '';
    document.getElementById('geographic_reach').value = p.geographic_reach || '';
    document.getElementById('history').value          = p.history || '';
    document.getElementById('leadership').value       = p.leadership || '';

    programs = data.programs || [];
    stats    = data.stats    || [];

    renderPrograms();
    renderStats();
  } catch (e) {
    showStatus('org-status', 'error', 'Could not load saved data: ' + e.message);
  }
}

async function saveOrgData() {
  clearStatus('org-status');
  showStatus('org-status', 'info', 'Saving…', true);
  try {
    await api('PUT', '/memory', {
      profile: {
        mission:          document.getElementById('mission').value,
        geographic_reach: document.getElementById('geographic_reach').value,
        history:          document.getElementById('history').value,
        leadership:       document.getElementById('leadership').value,
      },
      stats: stats.filter(s => s.label.trim() && s.value.trim()),
    });
    showStatus('org-status', 'success', 'Organization data saved.');
    setTimeout(() => clearStatus('org-status'), 3000);
  } catch (e) {
    showStatus('org-status', 'error', 'Save failed: ' + e.message);
  }
}


// ── Programs ─────────────────────────────────────────────────────────────────

function renderPrograms() {
  const list = document.getElementById('program-list');
  if (!programs.length) {
    list.innerHTML = '<p style="color:var(--gray-400);font-size:14px;margin-bottom:12px;">No programs added yet.</p>';
    return;
  }
  list.innerHTML = programs.map(p => `
    <div class="program-item">
      <div class="prog-info">
        <div class="prog-name">${esc(p.name)}</div>
        <div class="prog-meta">${[p.description, p.population].filter(Boolean).map(esc).join(' · ')}</div>
      </div>
      <div class="program-actions">
        <button class="btn btn-secondary btn-sm" onclick="openProgramModal(${p.id})">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteProgram(${p.id})">Remove</button>
      </div>
    </div>
  `).join('');
}

function openProgramModal(id) {
  const prog = id ? programs.find(p => p.id === id) : null;
  document.getElementById('modal-title').textContent = prog ? 'Edit Program' : 'Add Program';
  document.getElementById('modal-program-id').value  = prog ? prog.id : '';
  document.getElementById('modal-name').value        = prog ? prog.name : '';
  document.getElementById('modal-description').value = prog ? prog.description : '';
  document.getElementById('modal-outcomes').value    = prog ? prog.outcomes : '';
  document.getElementById('modal-population').value  = prog ? prog.population : '';
  document.getElementById('program-modal').classList.add('open');
}

function closeModal() {
  document.getElementById('program-modal').classList.remove('open');
}

async function saveProgram() {
  const id   = document.getElementById('modal-program-id').value;
  const name = document.getElementById('modal-name').value.trim();
  if (!name) { alert('Program name is required.'); return; }

  const data = {
    name,
    description: document.getElementById('modal-description').value,
    outcomes:    document.getElementById('modal-outcomes').value,
    population:  document.getElementById('modal-population').value,
  };

  try {
    if (id) {
      await api('PUT', `/programs/${id}`, data);
      const idx = programs.findIndex(p => p.id === parseInt(id));
      if (idx >= 0) programs[idx] = { id: parseInt(id), ...data };
    } else {
      const created = await api('POST', '/programs', data);
      programs.push(created);
    }
    renderPrograms();
    closeModal();
  } catch (e) {
    alert('Could not save program: ' + e.message);
  }
}

async function deleteProgram(id) {
  if (!confirm('Remove this program?')) return;
  try {
    await api('DELETE', `/programs/${id}`);
    programs = programs.filter(p => p.id !== id);
    renderPrograms();
  } catch (e) {
    alert('Could not remove program: ' + e.message);
  }
}

// Close modal on backdrop click
document.getElementById('program-modal').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeModal();
});


// ── Stats ─────────────────────────────────────────────────────────────────────

function renderStats() {
  const list = document.getElementById('stats-list');
  list.innerHTML = stats.map((s, i) => `
    <div class="stat-row">
      <input class="stat-label" type="text" placeholder="Label (e.g., People served annually)"
        value="${esc(s.label)}" oninput="stats[${i}].label = this.value" />
      <input class="stat-value" type="text" placeholder="Value (e.g., 1,200)"
        value="${esc(s.value)}" oninput="stats[${i}].value = this.value" />
      <button class="stat-remove" onclick="removeStat(${i})" title="Remove">×</button>
    </div>
  `).join('');
}

function addStatRow() {
  stats.push({ label: '', value: '' });
  renderStats();
  // Focus the new label input
  const rows = document.querySelectorAll('.stat-row');
  if (rows.length) rows[rows.length - 1].querySelector('.stat-label').focus();
}

function removeStat(i) {
  stats.splice(i, 1);
  renderStats();
}


// ── Document upload ──────────────────────────────────────────────────────────

const uploadZone = document.getElementById('upload-zone');
const fileInput  = document.getElementById('file-input');

uploadZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) uploadFile(fileInput.files[0]);
});

uploadZone.addEventListener('dragover', e => {
  e.preventDefault();
  uploadZone.classList.add('dragover');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('dragover');
  if (e.dataTransfer.files[0]) uploadFile(e.dataTransfer.files[0]);
});

async function uploadFile(file) {
  clearStatus('doc-status');
  showStatus('doc-status', 'info', `Uploading ${file.name}…`, true);

  const form = new FormData();
  form.append('file', file);

  try {
    const result = await api('POST', '/documents/upload', form);
    showStatus('doc-status', 'success',
      `"${result.filename}" uploaded — ${result.char_count.toLocaleString()} characters extracted.`);
    setTimeout(() => clearStatus('doc-status'), 4000);
    await loadDocuments();
  } catch (e) {
    showStatus('doc-status', 'error', 'Upload failed: ' + e.message);
  }
  fileInput.value = '';
}

async function loadDocuments() {
  try {
    const docs = await api('GET', '/documents');
    const list = document.getElementById('doc-list');
    if (!docs.length) {
      list.innerHTML = '<p style="color:var(--gray-400);font-size:14px;">No documents uploaded yet.</p>';
      return;
    }
    list.innerHTML = docs.map(d => `
      <div class="doc-item">
        <div>
          <div class="doc-name">${esc(d.filename)}</div>
          <div class="doc-meta">${d.char_count.toLocaleString()} characters · ${formatDate(d.uploaded_at)}</div>
        </div>
        <button class="btn btn-danger btn-sm" onclick="deleteDocument(${d.id}, '${esc(d.filename)}')">Remove</button>
      </div>
    `).join('');
  } catch (e) {
    // silently ignore — list just won't update
  }
}

async function deleteDocument(id, filename) {
  if (!confirm(`Remove "${filename}" from GrantPilot?`)) return;
  try {
    await api('DELETE', `/documents/${id}`);
    await loadDocuments();
  } catch (e) {
    alert('Could not remove document: ' + e.message);
  }
}


// ── Funder matching ──────────────────────────────────────────────────────────

async function runMatch() {
  const priorities = document.getElementById('funder-priorities').value.trim();
  if (!priorities) {
    showStatus('match-status', 'error', 'Please enter the funder\'s priority areas.');
    return;
  }

  const btn = document.getElementById('match-btn');
  btn.disabled = true;
  clearStatus('match-status');
  showStatus('match-status', 'info', 'Analyzing your organizational data… this takes a moment.', true);

  const output = document.getElementById('match-output');
  output.textContent = '';
  output.classList.add('empty');
  document.getElementById('copy-match-btn').style.display = 'none';
  document.getElementById('use-for-narrative-row').style.display = 'none';

  try {
    const result = await api('POST', '/match', { funder_priorities: priorities });
    output.textContent = result.matches;
    output.classList.remove('empty');
    document.getElementById('copy-match-btn').style.display = '';
    document.getElementById('use-for-narrative-row').style.display = '';
    clearStatus('match-status');
  } catch (e) {
    showStatus('match-status', 'error', e.message);
    output.textContent = '';
    output.classList.add('empty');
  } finally {
    btn.disabled = false;
  }
}

function sendToNarrative() {
  const matchText = document.getElementById('match-output').textContent;
  const priorities = document.getElementById('funder-priorities').value;
  document.getElementById('narrative-source').value  = matchText;
  document.getElementById('narrative-funder').value  = priorities;
  // Switch to narrative tab
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector('[data-tab="narrative"]').classList.add('active');
  document.getElementById('tab-narrative').classList.add('active');
}


// ── Narrative generation ──────────────────────────────────────────────────────

async function runNarrative() {
  const source  = document.getElementById('narrative-source').value.trim();
  const funder  = document.getElementById('narrative-funder').value.trim();
  const section = document.getElementById('section-type').value;
  const words   = parseInt(document.getElementById('word-count').value) || 300;

  if (!source) {
    showStatus('narrative-status', 'error', 'Please add matched content first. Run "Match to Funder" and use the "Use this content" button.');
    return;
  }

  const btn = document.getElementById('narrative-btn');
  btn.disabled = true;
  clearStatus('narrative-status');
  showStatus('narrative-status', 'info', 'Drafting your narrative… this takes a moment.', true);

  const output = document.getElementById('narrative-output');
  output.textContent = '';
  output.classList.add('empty');
  document.getElementById('copy-narrative-row').style.display = 'none';

  try {
    const result = await api('POST', '/narrative', {
      matched_content: source,
      funder_context:  funder,
      section_type:    section,
      word_count:      words,
    });
    output.textContent = result.narrative;
    output.classList.remove('empty');
    document.getElementById('copy-narrative-row').style.display = '';
    clearStatus('narrative-status');
  } catch (e) {
    showStatus('narrative-status', 'error', e.message);
  } finally {
    btn.disabled = false;
  }
}


// ── Copy to clipboard ────────────────────────────────────────────────────────

async function copyOutput(id) {
  const text = document.getElementById(id).textContent;
  try {
    await navigator.clipboard.writeText(text);
    // Brief visual feedback
    const btn = event.target;
    const orig = btn.textContent;
    btn.textContent = 'Copied!';
    setTimeout(() => { btn.textContent = orig; }, 1500);
  } catch {
    alert('Copy failed — please select and copy the text manually.');
  }
}


// ── Utilities ────────────────────────────────────────────────────────────────

function esc(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatDate(isoStr) {
  if (!isoStr) return '';
  try {
    return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch { return isoStr; }
}


// ── Init ─────────────────────────────────────────────────────────────────────

loadOrgData();
loadDocuments();
