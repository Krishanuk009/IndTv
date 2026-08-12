<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

$data = json_decode(file_get_contents('php://input'), true);
if (!validateCSRF($data['csrf_token'] ?? '')) sendResponse(false, null, 'CSRF Error', 403);

$path = sanitizePath($data['path'] ?? '');
$sha = $data['sha'] ?? '';

$payload = [
    'message' => "Delete $path",
    'sha' => $sha,
    'branch' => GITHUB_BRANCH
];

$res = githubRequest("contents/$path", 'DELETE', $payload);
sendResponse($res['status'] === 200, $res['body']);