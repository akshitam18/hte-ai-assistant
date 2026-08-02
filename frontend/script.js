// Base URL for the FastAPI backend
const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Element References
const sendBtn = document.getElementById('sendBtn');
const questionInput = document.getElementById('question');
const chatWindow = document.getElementById('chatWindow');
const pdfUpload = document.getElementById('pdfUpload');
const pdfList = document.getElementById('pdfList');
const docCount = document.getElementById('docCount');
const searchPdf = document.getElementById('searchPdf');

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
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (statusBadge && data.status === "running") {
            statusBadge.innerHTML = `<div class="status-dot"></div> RAG Engine Online`;
            statusBadge.style.borderColor = "rgba(16, 185, 129, 0.3)";
            statusBadge.style.color = "#34d399";
        }
    } catch (error) {
        console.error("Backend health check failed:", error);
        if (statusBadge) {
            statusBadge.innerHTML = `<div class="status-dot" style="background-color: #ef4444; box-shadow: 0 0 8px #ef4444;"></div> Backend Offline`;
            statusBadge.style.borderColor = "rgba(239, 68, 68, 0.3)";
            statusBadge.style.color = "#f87171";
        }
    }
}

// -------------------------------------------------------------
// FETCH EXISTING DOCUMENTS FROM BACKEND (/documents)
// -------------------------------------------------------------
async function fetchExistingDocuments() {
    if (!pdfList) return;

    try {
        const response = await fetch(`${API_BASE_URL}/documents`);
        if (!response.ok) throw new Error("Failed to fetch documents");

        const data = await response.json();
        pdfList.innerHTML = ''; // Clear temporary list

        const fileList = Array.isArray(data) ? data : (data.documents || []);

        fileList.forEach(fileObj => {
            const fileName = typeof fileObj === 'string' ? fileObj : (fileObj.name || fileObj.filename);
            if (!fileName) return;

            const li = document.createElement('li');
            li.className = 'doc-item';
            li.innerHTML = `
                <div class="doc-info">
                    <span class="doc-name" title="${escapeHTML(fileName)}">📄 ${escapeHTML(fileName)}</span>
                    <span class="doc-meta">Indexed</span>
                </div>
                <button class="btn-summarize" title="Summarize document">Summarize</button>
            `;

            // Attach summarize handler
            const summarizeBtn = li.querySelector('.btn-summarize');
            if (summarizeBtn) {
                summarizeBtn.addEventListener('click', () => summarizeDocument(fileName));
            }

            pdfList.appendChild(li);
        });

        updateDocCount();

    } catch (error) {
        console.error("Error loading existing documents:", error);
    }
}

// Run health check and fetch existing documents on page load
document.addEventListener("DOMContentLoaded", () => {
    checkBackendHealth();
    fetchExistingDocuments();
});

function escapeHTML(str) {
    return String(str).replace(/[&<>'"]/g,
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

// Helper to safely render Markdown content with fallbacks
function renderMarkdown(text) {
    if (typeof marked !== 'undefined' && marked.parse) {
        return marked.parse(text);
    }
    // Fallback if marked library fails to load
    return escapeHTML(text).replace(/\n/g, '<br>');
}

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
        if (chatWindow.contains(loadingDiv)) {
            chatWindow.removeChild(loadingDiv);
        }

        // Append AI Response
        const aiDiv = document.createElement('div');
        aiDiv.className = 'message ai';

        // Parse main markdown body
        let contentHTML = renderMarkdown(data.answer || "No response generated.");

        // Build source citation footer at the bottom if sources exist
        let citationHTML = "";
        if (data.source && data.source !== "None") {
            const pageInfo = data.page ? ` (Page ${data.page})` : '';
            citationHTML = `
                <div class="source-footer" style="margin-top:12px; padding-top:8px; border-top:1px solid #e2e8f0; font-size:0.8rem; color:#64748b;">
                    📌 <strong>Source Document:</strong> ${escapeHTML(data.source)}${pageInfo}
                </div>
            `;
        }

        aiDiv.innerHTML = `
            <strong style="color: #0f172a;">HTE AI Assistant</strong><br><br>
            ${contentHTML}
            ${citationHTML}
        `;
        chatWindow.appendChild(aiDiv);

    } catch (error) {
        console.error("Ask query error:", error);
        if (chatWindow.contains(loadingDiv)) {
            chatWindow.removeChild(loadingDiv);
        }

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

if (sendBtn) sendBtn.addEventListener('click', sendMessage);
if (questionInput) {
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Request Document Summary from Backend (/summarize/{filename})
async function summarizeDocument(filename) {
    // Append User Action Message to Chat
    const userDiv = document.createElement('div');
    userDiv.className = 'message user';
    userDiv.innerHTML = `<strong>You:</strong><br>Summarize <strong>${escapeHTML(filename)}</strong>`;
    chatWindow.appendChild(userDiv);

    // Show Loading Placeholder
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai';
    loadingDiv.innerHTML = `<em>📄 Generating summary for ${escapeHTML(filename)}...</em>`;
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch(`${API_BASE_URL}/summarize/${encodeURIComponent(filename)}`);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Failed to generate summary.");
        }

        const data = await response.json();
        
        if (chatWindow.contains(loadingDiv)) {
            chatWindow.removeChild(loadingDiv);
        }

        const aiDiv = document.createElement('div');
        aiDiv.className = 'message ai';
        
        // Parse summary with Markdown renderer
        const rawText = data.summary || data.answer || "No summary returned.";
        const formattedSummaryHTML = renderMarkdown(rawText);

        // Page info footer at bottom if supplied by API
        const pageInfo = data.page ? ` (Page ${data.page})` : '';

        aiDiv.innerHTML = `
            <strong style="color: #0f172a;">Executive Summary</strong><br><br>
            ${formattedSummaryHTML}
            <div class="source-footer" style="margin-top:12px; padding-top:8px; border-top:1px solid #e2e8f0; font-size:0.8rem; color:#64748b;">
                📄 <strong>Source Document:</strong> ${escapeHTML(filename)}${pageInfo}
            </div>
        `;
        chatWindow.appendChild(aiDiv);

    } catch (error) {
        console.error("Summarize error:", error);
        if (chatWindow.contains(loadingDiv)) {
            chatWindow.removeChild(loadingDiv);
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'message ai';
        errorDiv.innerHTML = `
            <strong>HTE AI Assistant</strong><br>
            <span style="color: #ef4444;">⚠️ Error: ${escapeHTML(error.message || "Could not generate summary.")}</span>
        `;
        chatWindow.appendChild(errorDiv);
    } finally {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

// Upload PDF Files to Backend (/upload)
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

                    // Refresh document list completely after upload completes
                    await fetchExistingDocuments();

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
                        <button class="doc-action-btn delete" title="Remove" style="background:none; border:none; cursor:pointer;">🗑️</button>
                    `;

                    const deleteBtn = tempLi.querySelector('.delete');
                    if (deleteBtn) {
                        deleteBtn.addEventListener('click', () => {
                            tempLi.remove();
                            updateDocCount();
                        });
                    }
                }
            }
        }

        pdfUpload.value = '';
    });
}

// Live Document Filtering in Sidebar
if (searchPdf) {
    searchPdf.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const items = pdfList.querySelectorAll('.doc-item');

        items.forEach(item => {
            const name = item.querySelector('.doc-name')?.textContent.toLowerCase() || '';
            if (name.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });
}