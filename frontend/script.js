// Base URL for the FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Element References
const sendBtn = document.getElementById('sendBtn');
const questionInput = document.getElementById('question');
const chatWindow = document.getElementById('chatWindow');
const pdfUpload = document.getElementById('pdfUpload');
const pdfList = document.getElementById('pdfList');
const docCount = document.getElementById('docCount');

// Update document counter in sidebar
function updateDocCount() {
    if (!docCount || !pdfList) return;
    const count = pdfList.children.length;
    docCount.textContent = `${count} ${count === 1 ? 'File' : 'Files'}`;
}

updateDocCount();

// Check backend connection health on page load
async function checkBackendHealth() {
    const statusBadge = document.querySelector('.status-badge');
    if (!statusBadge) return;

    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === "running") {
            statusBadge.innerHTML = `<div class="status-dot"></div> RAG Engine Online`;
            statusBadge.style.borderColor = "rgba(16, 185, 129, 0.3)";
            statusBadge.style.color = "#34d399";
        }
    } catch (error) {
        console.error("Backend health check failed:", error);
        statusBadge.innerHTML = `<div class="status-dot" style="background-color: #ef4444; box-shadow: 0 0 8px #ef4444;"></div> Backend Offline`;
        statusBadge.style.borderColor = "rgba(239, 68, 68, 0.3)";
        statusBadge.style.color = "#f87171";
    }
}

document.addEventListener("DOMContentLoaded", checkBackendHealth);

// Send Question to FastAPI Backend (/ask)
async function sendMessage() {
    const query = questionInput.value.trim();
    if (!query) return;

    // Append User Message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user';
    userDiv.innerHTML = `<strong>You:</strong><br>${escapeHTML(query)}`;
    chatWindow.appendChild(userDiv);

    questionInput.value = '';
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Show Loading Placeholder
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai';
    loadingDiv.innerHTML = `<em>⏳ Searching documents & generating answer...</em>`;
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Disable input while processing
    questionInput.disabled = true;
    if (sendBtn) sendBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: query })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error querying backend.");
        }

        const data = await response.json();

        // Remove Loading Placeholder
        chatWindow.removeChild(loadingDiv);

        // Append AI Response
        const aiDiv = document.createElement('div');
        aiDiv.className = 'message ai';

        let citationHTML = "";
        if (data.source && data.source !== "None") {
            citationHTML = `<span class="citation">📌 Source: ${escapeHTML(data.source)} (Page ${data.page})</span>`;
        }

        aiDiv.innerHTML = `
            <strong>HTE AI Assistant</strong><br>
            ${escapeHTML(data.answer)}
            ${citationHTML}
        `;
        chatWindow.appendChild(aiDiv);

    } catch (error) {
        console.error("Ask query error:", error);
        chatWindow.removeChild(loadingDiv);

        const errorDiv = document.createElement('div');
        errorDiv.className = 'message ai';
        errorDiv.innerHTML = `
            <strong>HTE AI Assistant</strong><br>
            <span style="color: #ef4444;">⚠️ Error: ${escapeHTML(error.message || "Failed to retrieve answer from assistant.")}</span>
        `;
        chatWindow.appendChild(errorDiv);
    } finally {
        questionInput.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        questionInput.focus();
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

sendBtn.addEventListener('click', sendMessage);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Upload PDF Files to Backend (/upload) - Handled strictly within the sidebar
if (pdfUpload) {
    pdfUpload.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (!files.length) return;

        for (let file of Array.from(files)) {
            if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {

                const formData = new FormData();
                formData.append("file", file);

                // Create placeholder in sidebar list during upload
                const tempLi = document.createElement('li');
                tempLi.className = 'doc-item';
                tempLi.style.opacity = '0.7';
                tempLi.innerHTML = `
                    <div class="doc-info">
                        <span class="doc-name">⏳ Uploading ${escapeHTML(file.name)}...</span>
                        <span class="doc-meta">Indexing document...</span>
                    </div>
                `;
                pdfList.appendChild(tempLi);
                updateDocCount();
                pdfList.scrollTop = pdfList.scrollHeight;

                try {
                    const response = await fetch(`${API_BASE_URL}/upload`, {
                        method: "POST",
                        body: formData
                    });

                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.detail || "Upload failed.");
                    }

                    const data = await response.json();

                    // Update sidebar item upon successful upload
                    tempLi.style.opacity = '1';
                    tempLi.innerHTML = `
                        <input type="checkbox" checked title="Include in search context" />
                        <div class="doc-info">
                            <span class="doc-name">📄 ${escapeHTML(data.filename)}</span>
                            <span class="doc-meta">${(file.size / 1024).toFixed(1)} KB</span>
                        </div>
                        <button class="doc-action-btn delete" title="Delete">🗑️</button>
                    `;

                    const deleteBtn = tempLi.querySelector('.delete');
                    deleteBtn.addEventListener('click', () => {
                        tempLi.remove();
                        updateDocCount();
                    });

                } catch (error) {
                    console.error("Upload error:", error);

                    // Show error state in sidebar card
                    tempLi.style.borderColor = '#ef4444';
                    tempLi.style.background = '#fef2f2';
                    tempLi.style.opacity = '1';
                    tempLi.innerHTML = `
                        <div class="doc-info">
                            <span class="doc-name" style="color: #ef4444;">❌ ${escapeHTML(file.name)}</span>
                            <span class="doc-meta" style="color: #ef4444;">${escapeHTML(error.message)}</span>
                        </div>
                        <button class="doc-action-btn delete" title="Remove">🗑️</button>
                    `;

                    const deleteBtn = tempLi.querySelector('.delete');
                    deleteBtn.addEventListener('click', () => {
                        tempLi.remove();
                        updateDocCount();
                    });
                }
            }
        }

        updateDocCount();
        pdfUpload.value = '';
    });
}

function escapeHTML(str) {
    return String(str).replace(/[&<>'"]/g,
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}
