<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

if (!validateCSRF($_POST['csrf_token'] ?? '')) {
    sendResponse(false, null, 'Invalid CSRF', 403);
}

$destPath = sanitizePath($_POST['path'] ?? '');
$file = $_FILES['file'];
$fileName = basename($file['name']);
$finalPath = ($destPath ? $destPath . '/' : '') . $fileName;

$content = base64_encode(file_get_contents($file['tmp_name']));

$payload = [
    'message' => "Upload $fileName",
    'content' => $content,
    'branch' => GITHUB_BRANCH
];

$res = githubRequest("contents/$finalPath", 'PUT', $payload);

if ($res['status'] === 201 || $res['status'] === 200) {
    sendResponse(true);
} else {
    sendResponse(false, null, $res['body']['message'] ?? 'Upload failed', $res['status']);
}