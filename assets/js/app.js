document.addEventListener('DOMContentLoaded', () => {
    // Initial Load of root directory
    FileManager.load('');

    // --- Sidebar & Mobile Navigation ---
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const menuBtn = document.getElementById('menuBtn');

    const closeAllOverlays = () => {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        // Also close Action Sheet if it's open
        const actionSheet = document.getElementById('actionSheet');
        if (actionSheet) actionSheet.classList.remove('active');
    };

    menuBtn.onclick = () => {
        sidebar.classList.add('active');
        overlay.classList.add('active');
    };

    // Close sidebar or action menu when clicking the dark overlay
    overlay.onclick = closeAllOverlays;

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.onclick = () => {
            const isLight = document.body.classList.toggle('light-mode');
            localStorage.setItem('gh-manager-theme', isLight ? 'light' : 'dark');
            showToast(isLight ? 'Light Mode enabled' : 'Dark Mode enabled');
        };
    }
    // Restore saved theme
    if (localStorage.getItem('gh-manager-theme') === 'light') {
        document.body.classList.add('light-mode');
    }

    // --- Action Sheet (Bottom Menu) Bindings ---
    // These link the buttons in the mobile menu to the FileManager logic
    const actEdit = document.getElementById('actEdit');
    const actRename = document.getElementById('actRename');
    const actDelete = document.getElementById('actDelete');

    if (actEdit) actEdit.onclick = () => FileManager.edit(FileManager.selected);
    if (actRename) actRename.onclick = () => FileManager.rename();
    if (actDelete) actDelete.onclick = () => FileManager.delete();

    // --- Editor Controls ---
    document.getElementById('closeEditor').onclick = () => {
        document.getElementById('editorModal').style.display = 'none';
    };

    document.getElementById('formatJsonBtn').onclick = () => {
        const area = document.getElementById('codeArea');
        try {
            area.value = JSON.stringify(JSON.parse(area.value), null, 4);
            showToast('JSON Formatted');
        } catch(e) {
            showToast('Invalid JSON format', 'error');
        }
    };

    document.getElementById('saveFileBtn').onclick = async () => {
        const modal = document.getElementById('editorModal');
        const content = document.getElementById('codeArea').value;
        
        showToast('Saving to GitHub...');
        try {
            const res = await fetch('api/file_save.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: modal.dataset.path,
                    sha: modal.dataset.sha,
                    content: content,
                    csrf_token: CSRF_TOKEN
                })
            });
            const json = await res.json();
            if (json.success) {
                showToast('File saved successfully');
                modal.dataset.sha = json.sha; // Update SHA for next save
            } else {
                showToast(json.error || 'Save failed', 'error');
            }
        } catch (e) {
            showToast('Network error while saving', 'error');
        }
    };

    // --- Standard File Upload ---
    const fileInput = document.getElementById('fileInput');
    document.getElementById('uploadTrigger').onclick = () => fileInput.click();

    fileInput.onchange = async (e) => {
        if (e.target.files.length === 0) return;
        
        for (let file of e.target.files) {
            showToast('Uploading: ' + file.name);
            const fd = new FormData();
            fd.append('file', file);
            fd.append('path', FileManager.currentPath);
            fd.append('csrf_token', CSRF_TOKEN);
            
            try {
                const res = await fetch('api/file_upload.php', { method: 'POST', body: fd });
                const json = await res.json();
                if (json.success) showToast(file.name + ' uploaded');
                else showToast(json.error, 'error');
            } catch (err) {
                showToast('Upload failed: ' + file.name, 'error');
            }
        }
        FileManager.load(FileManager.currentPath);
        e.target.value = ''; // Reset input
    };

    // --- ZIP Extraction Logic ---
    const zipInput = document.getElementById('zipInput');
    if (zipInput) {
        zipInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const loader = document.getElementById('extractLoader');
            loader.style.display = 'flex';

            const fd = new FormData();
            fd.append('zipfile', file);
            fd.append('path', FileManager.currentPath);
            fd.append('csrf_token', CSRF_TOKEN);

            try {
                const res = await fetch('api/file_extract.php', { method: 'POST', body: fd });
                const json = await res.json();
                if (json.success) {
                    showToast(`Syncing complete: ${json.files} files added`);
                    FileManager.load(FileManager.currentPath);
                } else {
                    showToast(json.error || 'Extraction failed', 'error');
                }
            } catch (err) {
                showToast('Server error during extraction', 'error');
            } finally {
                loader.style.display = 'none';
                e.target.value = ''; // Reset input
            }
        };
    }

    // --- Folder Creation ---
    document.getElementById('newFolderBtn').onclick = async () => {
        const name = prompt('Enter New Folder Name:');
        if (!name || name.trim() === '') return;

        showToast('Creating folder...');
        try {
            const res = await fetch('api/folder_create.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    path: FileManager.currentPath + '/' + name.trim(), 
                    csrf_token: CSRF_TOKEN 
                })
            });
            const json = await res.json();
            if (json.success) {
                showToast('Folder created');
                FileManager.load(FileManager.currentPath);
            } else {
                showToast(json.error || 'Folder creation failed', 'error');
            }
        } catch (e) {
            showToast('Connection error', 'error');
        }
    };

    // --- Search Filtering ---
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.oninput = (e) => {
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.file-card');
            
            cards.forEach(card => {
                const fileName = card.querySelector('span').innerText.toLowerCase();
                // Don't filter out the "Go Back" folder
                if (fileName === 'go back') {
                    card.style.display = 'flex';
                    return;
                }
                card.style.display = fileName.includes(query) ? 'flex' : 'none';
            });
        };
    }
});