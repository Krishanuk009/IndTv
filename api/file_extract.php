<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';

set_time_limit(300); // Give InfinityFree more time to process

if (!isset($_FILES['zipfile'])) {
    die(json_encode(['success' => false, 'error' => 'No file']));
}

$zipFile = $_FILES['zipfile']['tmp_name'];
$targetPath = isset($_POST['path']) ? trim($_POST['path'], '/') . '/' : '';
if ($targetPath === '/') $targetPath = '';

$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    $tempDir = '../uploads/extract_' . uniqid();
    if (!is_dir($tempDir)) mkdir($tempDir, 0777, true);
    
    $zip->extractTo($tempDir);
    $zip->close();

    $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($tempDir));
    $success = 0;

    foreach ($iterator as $file) {
        if ($file->isDir()) continue;

        $filePath = $file->getPathname();
        $relativePath = str_replace(realpath($tempDir), '', realpath($filePath));
        $relativePath = ltrim(str_replace('\\', '/', $relativePath), '/');
        
        $githubPath = $targetPath . $relativePath;
        $content = base64_encode(file_get_contents($filePath));

        // Sync to GitHub
        $res = githubRequest("contents/$githubPath", 'PUT', [
            'message' => "Extracted: $relativePath",
            'content' => $content,
            'branch' => GITHUB_BRANCH
        ]);

        if ($res['status'] === 201 || $res['status'] === 200) $success++;
    }

    // Recursive Cleanup
    $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($tempDir, RecursiveDirectoryIterator::SKIP_DOTS), RecursiveIteratorIterator::CHILD_FIRST);
    foreach ($files as $fileinfo) {
        $todo = ($fileinfo->isDir() ? 'rmdir' : 'unlink');
        $todo($fileinfo->getRealPath());
    }
    rmdir($tempDir);

    echo json_encode(['success' => true, 'files' => $success]);
} else {
    echo json_encode(['success' => false, 'error' => 'Invalid ZIP']);
}