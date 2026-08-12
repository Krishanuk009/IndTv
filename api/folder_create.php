<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

$data = json_decode(file_get_contents('php://input'), true);
if (!validateCSRF($data['csrf_token'] ?? '')) sendResponse(false, null, 'CSRF Error', 403);

$path = sanitizePath($data['path'] ?? '');
$placeholder = $path . '/.gitkeep';

$payload = [
    'message' => "Create folder $path",
    'content' => base64_encode("Directory placeholder"),
    'branch' => GITHUB_BRANCH
];

$res = githubRequest("contents/$placeholder", 'PUT', $payload);
sendResponse($res['status'] === 201);