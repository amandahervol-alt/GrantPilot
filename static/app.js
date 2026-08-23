document.addEventListener('DOMContentLoaded', () => {

    // Global state
    let matchedItemsCache = [];

    // Initialize data
    loadOrgData();
    loadDocuments();

    // ----------------------------------------------------
    // 1. Organizational Memory Handlers
    // ----------------------------------------------------
    const orgForm = document.getElementById('org-memory-form');
    const orgStatus = document.getElementById('org-status');
    const saveOrgBtn = document.getElementById('save-org-btn');

    async function loadOrgData() {
        try {
            const res = await fetch('/api/org/load');
            if (res.ok) {
                const data = await res.json();
                if (data.mission) document.getElementById('mission').value = data.mission;
                if (data.programs) document.getElementById('programs').value = data.programs;
                if (data.outcomes) document.getElementById('outcomes').value = data.outcomes;
                if (data.stats) document.getElementById('stats').value = data.stats;
            }
        } catch (err) {
            console.error('Failed to load initial org memory:', err);
        }
    }

    orgForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const mission = document.getElementById('mission').value;
        const programs = document.getElementById('programs').value;
        const outcomes = document.getElementById('outcomes').value;
        const stats = document.getElementById('stats').value;

        setLoading(saveOrgBtn, orgStatus, 'Saving organizational memory...');

        try {
            const res = await fetch('/api/org/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mission, programs, outcomes, stats })
            });
            const data = await res.json();

            if (res.ok) {
                setStatus(orgStatus, data.message || 'Organizational data saved!', 'success');
            } else {
                setStatus(orgStatus, data.detail || 'Failed to save organizational data.', 'error');
            }
        } catch (err) {
            setStatus(orgStatus, 'Network error. Could not connect to server.', 'error');
        } finally {
            resetButton(saveOrgBtn, '💾 Save Baseline Memory');
        }
    });

    // ----------------------------------------------------
    // 2. Document Ingestion Handlers
    // ----------------------------------------------------
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const docUploadStatus = document.getElementById('doc-upload-status');
    const docsList = document.getElementById('docs-list');

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            uploadFile(fileInput.files[0]);
        }
    });

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        setStatus(docUploadStatus, `Uploading and indexing '${file.name}'...`, 'loading');

        try {
            const res = await fetch('/api/documents/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                setStatus(docUploadStatus, data.message, 'success');
                loadDocuments();
            } else {
                setStatus(docUploadStatus, data.detail || 'Upload failed.', 'error');
            }
        } catch (err) {
            setStatus(docUploadStatus, 'Network error during upload.', 'error');
        } finally {
            fileInput.value = '';
        }
    }

    async function loadDocuments() {
        try {
            const res = await fetch('/api/documents');
            if (res.ok) {
                const data = await res.json();
                renderDocumentsList(data.documents || []);
            }
        } catch (err) {
            console.error('Failed to load documents:', err);
        }
    }

    function renderDocumentsList(docs) {
        docsList.innerHTML = '';
        if (docs.length === 0) {
            docsList.innerHTML = '<p class="text-muted empty-hint">No supporting documents uploaded yet.</p>';
            return;
        }

        docs.forEach(doc => {
            const el = document.createElement('div');
            el.className = 'doc-pill';
            el.innerHTML = `
                <div class="doc-info">
                    <span>📄</span>
                    <strong>${escapeHtml(doc.filename)}</strong>
                    <span class="doc-badge">${doc.word_count.toLocaleString()} words</span>
                </div>
                <button class="delete-doc-btn" data-id="${doc.id}" title="Remove document">✕</button>
            `;

            el.querySelector('.delete-doc-btn').addEventListener('click', async (e) => {
                const docId = e.target.getAttribute('data-id');
                if (confirm(`Remove '${doc.filename}' from knowledge base?`)) {
                    await deleteDocument(docId);
                }
            });

            docsList.appendChild(el);
        });
    }

    async function deleteDocument(docId) {
        try {
            const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
            if (res.ok) {
                loadDocuments();
            }
        } catch (err) {
            console.error('Failed to delete document:', err);
        }
    }

    // ----------------------------------------------------
    // 3. Funder Alignment Matching Handlers
    // ----------------------------------------------------
    const matchForm = document.getElementById('funder-match-form');
    const matchStatus = document.getElementById('match-status');
    const matchBtn = document.getElementById('match-btn');
    const resultsContainer = document.getElementById('results-container');
    const matchesList = document.getElementById('matches-list');
    const useAllMatchesBtn = document.getElementById('use-all-matches-btn');

    matchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const funderPriorities = document.getElementById('funder-priorities').value;

        setLoading(matchBtn, matchStatus, 'Analyzing alignment with AI...');
        resultsContainer.classList.add('hidden');

        try {
            const res = await fetch('/api/funder/match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ funder_priorities: funderPriorities })
            });
            const data = await res.json();

            if (res.ok) {
                matchedItemsCache = data.matches || [];
                renderMatches(matchedItemsCache);
                setStatus(matchStatus, `Analysis complete. Identified ${matchedItemsCache.length} alignment areas.`, 'success');
                
                // Pre-fill target funder focus in Narrative generator
                const narrativeFunderInput = document.getElementById('narrative-funder-context');
                if (!narrativeFunderInput.value.trim()) {
                    narrativeFunderInput.value = funderPriorities.slice(0, 100);
                }
            } else {
                setStatus(matchStatus, data.detail || 'Error during AI analysis.', 'error');
            }
        } catch (err) {
            setStatus(matchStatus, 'Network error or server unreachable.', 'error');
        } finally {
            resetButton(matchBtn, '⚡ Analyze Alignment');
        }
    });

    function renderMatches(matches) {
        matchesList.innerHTML = '';
        if (matches.length === 0) {
            matchesList.innerHTML = '<p class="text-muted">No high-confidence overlaps identified. Check your organizational memory or document store.</p>';
        } else {
            matches.sort((a, b) => a.rank - b.rank);
            matches.forEach(match => {
                const el = document.createElement('div');
                el.className = 'match-item';
                el.innerHTML = `
                    <div class="match-rank">Alignment Rank #${match.rank}</div>
                    <div class="match-content">"${escapeHtml(match.content)}"</div>
                    <div class="match-explanation">${escapeHtml(match.explanation)}</div>
                `;
                matchesList.appendChild(el);
            });
        }
        resultsContainer.classList.remove('hidden');
    }

    useAllMatchesBtn.addEventListener('click', () => {
        document.getElementById('card-narrative').scrollIntoView({ behavior: 'smooth' });
        showToast('Matched highlights added to draft context!');
    });

    // ----------------------------------------------------
    // 4. Narrative Draft Generator Handlers
    // ----------------------------------------------------
    const narrativeForm = document.getElementById('narrative-form');
    const generateDraftBtn = document.getElementById('generate-draft-btn');
    const narrativeStatus = document.getElementById('narrative-status');
    const draftContainer = document.getElementById('draft-container');
    const draftSectionTitle = document.getElementById('draft-section-title');
    const draftWordBadge = document.getElementById('draft-word-badge');
    const draftText = document.getElementById('draft-text');
    const gapsBanner = document.getElementById('gaps-banner');
    const gapsList = document.getElementById('gaps-list');
    const copyDraftBtn = document.getElementById('copy-draft-btn');

    narrativeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const sectionType = document.getElementById('section-type').value;
        const targetWordCount = parseInt(document.getElementById('word-count').value, 10);
        const funderContext = document.getElementById('narrative-funder-context').value;
        const matchedPoints = matchedItemsCache.map(m => m.content);

        setLoading(generateDraftBtn, narrativeStatus, `Drafting ${sectionType}...`);
        draftContainer.classList.add('hidden');
        gapsBanner.classList.add('hidden');

        try {
            const res = await fetch('/api/narrative/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    section_type: sectionType,
                    target_word_count: targetWordCount,
                    funder_context: funderContext,
                    matched_points: matchedPoints
                })
            });
            const data = await res.json();

            if (res.ok) {
                draftSectionTitle.innerText = `${data.section_type} Draft`;
                draftWordBadge.innerText = `${data.actual_word_count} words`;
                draftText.innerText = data.draft;

                // Render gaps if present
                if (data.gaps && data.gaps.length > 0) {
                    gapsList.innerHTML = '';
                    data.gaps.forEach(gap => {
                        const li = document.createElement('li');
                        li.innerText = gap;
                        gapsList.appendChild(li);
                    });
                    gapsBanner.classList.remove('hidden');
                }

                draftContainer.classList.remove('hidden');
                setStatus(narrativeStatus, 'Draft generated successfully!', 'success');
            } else {
                setStatus(narrativeStatus, data.detail || 'Failed to generate narrative.', 'error');
            }
        } catch (err) {
            setStatus(narrativeStatus, 'Network error or server unreachable.', 'error');
        } finally {
            resetButton(generateDraftBtn, '✨ Generate Grounded Draft');
        }
    });

    // Copy to clipboard
    copyDraftBtn.addEventListener('click', async () => {
        const text = draftText.innerText;
        if (!text) return;

        try {
            await navigator.clipboard.writeText(text);
            showToast('Draft copied to clipboard!');
        } catch (err) {
            console.error('Clipboard copy failed:', err);
        }
    });

    // ----------------------------------------------------
    // UI Helpers
    // ----------------------------------------------------
    function setLoading(btn, statusEl, msg) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = `<span>⏳ ${msg}</span>`;
        statusEl.className = 'status-message loading';
        statusEl.innerText = msg;
    }

    function resetButton(btn, defaultHtml) {
        btn.disabled = false;
        btn.innerHTML = `<span>${defaultHtml}</span>`;
    }

    function setStatus(statusEl, msg, type) {
        statusEl.className = `status-message ${type}`;
        statusEl.innerText = msg;
    }

    function showToast(msg) {
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
});
