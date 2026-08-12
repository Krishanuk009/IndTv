const FileManager = {
    currentPath: '',
    items: [],
    selected: null,

    async load(path = '') {
        const list = document.getElementById('fileList');
        list.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:50px"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';
        try {
            const res = await fetch(`api/contents.php?path=${encodeURIComponent(path)}`);
            const json = await res.json();
            if (json.success) {
                this.currentPath = path;
                this.items = Array.isArray(json.items) ? json.items : [json.items];
                this.render();
                this.renderBC();
            } else showToast(json.error, 'error');
        } catch (e) { showToast('Connection Error', 'error'); }
    },

    render() {
        const list = document.getElementById('fileList');
        list.innerHTML = '';
        if (this.currentPath) {
            list.appendChild(this.createCard({ name: '..', type: 'dir', path: this.currentPath.split('/').slice(0,-1).join('/') }, true));
        }
        this.items.sort((a,b) => (b.type==='dir') - (a.type==='dir')).forEach(item => {
            list.appendChild(this.createCard(item));
        });
    },

    createCard(item, isBack = false) {
        const div = document.createElement('div');
        div.className = 'file-card';
        let icon = item.type === 'dir' ? 'fa-folder' : 'fa-file-lines';
        let color = item.type === 'dir' ? '#e3b341' : '#58a6ff';
        
        div.innerHTML = `
            <i class="fas ${isBack ? 'fa-arrow-turn-up' : icon}" style="color:${isBack ? 'var(--accent)' : color}"></i>
            <span>${isBack ? 'Go Back' : item.name}</span>
            ${!isBack ? '<div class="card-menu"><i class="fas fa-ellipsis-vertical"></i></div>' : ''}
        `;

        div.onclick = (e) => {
            if (e.target.closest('.card-menu')) {
                e.stopPropagation();
                this.openMenu(item);
            } else {
                item.type === 'dir' ? this.load(item.path) : this.edit(item);
            }
        };
        return div;
    },

    openMenu(item) {
        this.selected = item;
        document.getElementById('sheetItemName').innerText = item.name;
        document.getElementById('sheetIcon').className = 'fas ' + (item.type === 'dir' ? 'fa-folder' : 'fa-file');
        document.getElementById('actionSheet').classList.add('active');
        document.getElementById('sidebarOverlay').classList.add('active');
    },

    closeMenu() {
        document.getElementById('actionSheet').classList.remove('active');
        document.getElementById('sidebarOverlay').classList.remove('active');
    },

    async edit(item) {
        showToast('Opening...');
        const res = await fetch(`api/file_read.php?path=${encodeURIComponent(item.path)}`);
        const json = await res.json();
        if (json.success) {
            document.getElementById('editorFileName').innerText = item.name;
            document.getElementById('codeArea').value = json.content;
            const ed = document.getElementById('editorModal');
            ed.dataset.path = item.path;
            ed.dataset.sha = json.sha;
            ed.style.display = 'flex';
            this.closeMenu();
        }
    },

    async delete() {
        if (!confirm(`Delete ${this.selected.name}?`)) return;
        showToast('Deleting...');
        const res = await fetch('api/file_delete.php', {
            method: 'POST',
            body: JSON.stringify({ path: this.selected.path, sha: this.selected.sha, csrf_token: CSRF_TOKEN })
        });
        const json = await res.json();
        if (json.success) { showToast('Deleted'); this.load(this.currentPath); this.closeMenu(); }
    },

    async rename() {
        const newName = prompt('New name:', this.selected.name);
        if (!newName || newName === this.selected.name) return;
        showToast('Renaming...');
        const res = await fetch('api/file_rename.php', {
            method: 'POST',
            body: JSON.stringify({ path: this.selected.path, newName, sha: this.selected.sha, csrf_token: CSRF_TOKEN })
        });
        const json = await res.json();
        if (json.success) { showToast('Renamed'); this.load(this.currentPath); this.closeMenu(); }
        else showToast(json.error, 'error');
    },

    renderBC() {
        const bc = document.getElementById('breadcrumb');
        const parts = this.currentPath.split('/').filter(p => p);
        let html = '<span onclick="FileManager.load(\'\')">root</span>';
        let acc = '';
        parts.forEach(p => {
            acc += (acc ? '/' : '') + p;
            html += ` / <span onclick="FileManager.load('${acc}')">${p}</span>`;
        });
        bc.innerHTML = html;
    }
};