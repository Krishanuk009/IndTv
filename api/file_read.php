<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

$path = sanitizePath($_GET['path'] ?? '');
$res = githubRequest("contents/$path?ref=" . GITHUB_BRANCH);

if ($res['status'] === 200) {
    $content = isset($res['body']['content']) ? base64_decode($res['body']['content']) : '';
    sendResponse(true, ['content' => $content, 'sha' => $res['body']['sha']]);
} else {
    sendResponse(false, null, 'Error reading file', $res['status']);
}