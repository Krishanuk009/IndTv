<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

$path = sanitizePath($_GET['path'] ?? '');
$res = githubRequest("contents/$path?ref=" . GITHUB_BRANCH);

if ($res['status'] === 200) {
    sendResponse(true, $res['body']);
} else {
    sendResponse(false, null, $res['body']['message'] ?? 'Not found', $res['status']);
}