// DOM Element References
const sendBtn = document.getElementById('sendBtn');
const questionInput = document.getElementById('question');
const chatWindow = document.getElementById('chatWindow');
const pdfUpload = document.getElementById('pdfUpload');
const pdfList = document.getElementById('pdfList');
const docCount = document.getElementById('docCount');

function updateDocCount() {
    if (!docCount || !pdfList) return;
    const count = pdfList.children.length;
    docCount.textContent = `${count} ${count === 1 ? 'File' : 'Files'}`;
}

updateDocCount();

function sendMessage() {
    const query = questionInput.value.trim();
    if (!query) return;


    const userDiv = document.createElement('div');
    userDiv.className = 'message user';
    userDiv.innerHTML = `<strong>You:</strong><br>${escapeHTML(query)}`;
    chatWindow.appendChild(userDiv);


    questionInput.value = '';
    chatWindow.scrollTop = chatWindow.scrollHeight;


    setTimeout(() => {
        const aiDiv = document.createElement('div');
        aiDiv.className = 'message ai';
        aiDiv.innerHTML = `
            <strong>HTE AI Assistant</strong><br>
            Information regarding "${escapeHTML(query)}" has been retrieved based on current Higher & Technical Education norms.
            <span class="citation">📌 Source: Government Resolution & Guidelines (Page 14)</span>
        `;
        chatWindow.appendChild(aiDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }, 600);
}

sendBtn.addEventListener('click', sendMessage);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

if (pdfUpload) {
    pdfUpload.addEventListener('change', (e) => {
        const files = e.target.files;
        if (!files.length) return;

        Array.from(files).forEach(file => {
            if (file.type === "application/pdf") {
                const li = document.createElement('li');
                li.className = 'doc-item';
               
                li.innerHTML = `
                    <input type="checkbox" checked title="Include in search context" />
                    <div class="doc-info">
                        <span class="doc-name">📄 ${file.name}</span>
                        <span class="doc-meta">${(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button class="doc-action-btn delete" title="Delete">🗑️</button>
                `;

                const deleteBtn = li.querySelector('.delete');
                deleteBtn.addEventListener('click', () => {
                    li.remove();
                    updateDocCount();
                });

                pdfList.appendChild(li);
            }
        });
        updateDocCount();
        pdfUpload.value = '';
    });
}
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g,
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}
