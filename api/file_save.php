<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

$data = json_decode(file_get_contents('php://input'), true);

if (!validateCSRF($data['csrf_token'] ?? '')) {
    sendResponse(false, null, 'Invalid CSRF', 403);
}

$path = sanitizePath($data['path'] ?? '');
$content = $data['content'] ?? '';
$sha = $data['sha'] ?? '';
$message = $data['message'] ?? 'Update via Web Manager';

$payload = [
    'message' => $message,
    'content' => base64_encode($content),
    'sha' => $sha,
    'branch' => GITHUB_BRANCH
];

$res = githubRequest("contents/$path", 'PUT', $payload);

if ($res['status'] === 200 || $res['status'] === 201) {
    sendResponse(true, $res['body']);
} else {
    sendResponse(false, null, $res['body']['message'] ?? 'Save failed', $res['status']);
}