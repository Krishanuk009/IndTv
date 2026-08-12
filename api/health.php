<?php
require_once '../includes/auth.php';
requireAuth();
require_once '../includes/github.php';
require_once '../includes/security.php';

$res = githubRequest(''); // Base repo info
if ($res['status'] === 200) {
    sendResponse(true, ['status' => 'Connected', 'repo' => $res['body']['full_name']]);
} else {
    sendResponse(false, null, 'GitHub connection failed', $res['status']);
}