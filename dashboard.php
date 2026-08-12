<?php
require_once 'includes/auth.php';
requireAuth();
require_once 'config/config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Explorer | <?= APP_NAME ?></title>
    <link rel="stylesheet" href="assets/css/app.css?v=<?= time() ?>">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="dark-mode">
    <div class="overlay" id="sidebarOverlay"></div>

    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header"><i class="fab fa-github"></i> <span>GH Manager</span></div>
            <nav class="nav-links">
                <div class="nav-item active" onclick="FileManager.load('')"><i class="fas fa-folder-tree"></i> Explorer</div>
                <div class="nav-item" onclick="document.getElementById('zipInput').click()"><i class="fas fa-file-archive"></i> Extract ZIP</div>
                <div class="nav-item" id="themeToggle"><i class="fas fa-moon"></i> Theme</div>
                <div class="nav-item" style="color: var(--danger)" onclick="location.href='logout.php'"><i class="fas fa-power-off"></i> Logout</div>
            </nav>
            <div class="sidebar-footer">Repo: <?= GITHUB_REPOSITORY ?></div>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <header class="top-bar">
                <div class="bar-left">
                    <button class="icon-btn" id="menuBtn"><i class="fas fa-bars-staggered"></i></button>
                    <div class="breadcrumb" id="breadcrumb">/ root</div>
                </div>
                <div class="bar-right">
                    <button class="btn btn-primary" id="uploadTrigger"><i class="fas fa-cloud-arrow-up"></i> <span class="hide-mobile">Upload</span></button>
                </div>
            </header>

            <div class="explorer">
                <div class="search-bar">
                    <i class="fas fa-search"></i>
                    <input type="text" id="searchInput" placeholder="Search in this folder...">
                    <button class="icon-btn" id="newFolderBtn"><i class="fas fa-folder-plus"></i></button>
                </div>
                <div class="file-grid" id="fileList"></div>
            </div>
        </main>
    </div>

    <!-- Mobile Action Sheet (Bottom Menu) -->
    <div class="action-sheet" id="actionSheet">
        <div class="sheet-handle"></div>
        <div class="sheet-header">
            <i id="sheetIcon" class="fas fa-file"></i>
            <span id="sheetItemName">filename.ext</span>
        </div>
        <div class="action-list">
            <div class="action-item" id="actEdit"><i class="fas fa-pen-to-square"></i> Edit Content</div>
            <div class="action-item" id="actRename"><i class="fas fa-i-cursor"></i> Rename</div>
            <div class="action-item danger" id="actDelete"><i class="fas fa-trash-can"></i> Delete</div>
        </div>
    </div>

    <!-- Editor Modal -->
    <div class="editor-modal" id="editorModal">
        <div class="editor-header">
            <button class="icon-btn" id="closeEditor"><i class="fas fa-xmark"></i></button>
            <span id="editorFileName"></span>
            <button class="btn btn-primary" id="saveFileBtn">Save</button>
        </div>
        <textarea id="codeArea" spellcheck="false"></textarea>
    </div>

    <!-- ZIP Extraction Loader -->
    <div class="loading-overlay" id="extractLoader">
        <div class="loader-box">
            <i class="fas fa-circle-notch fa-spin fa-3x"></i>
            <h3>Syncing with GitHub...</h3>
            <p>Processing ZIP contents. Do not close.</p>
        </div>
    </div>

    <input type="file" id="fileInput" multiple hidden>
    <input type="file" id="zipInput" accept=".zip" hidden>

    <script>const CSRF_TOKEN = '<?= $_SESSION['csrf_token'] ?>';</script>
    <script src="assets/js/notifications.js"></script>
    <script src="assets/js/file-manager.js?v=<?= time() ?>"></script>
    <script src="assets/js/app.js?v=<?= time() ?>"></script>
</body>
</html>