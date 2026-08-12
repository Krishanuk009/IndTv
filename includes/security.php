<?php
function validateCSRF($token) {
    return isset($_SESSION['csrf_token']) && hash_equals($_SESSION['csrf_token'], $token);
}

function sanitizePath($path) {
    // Remove leading/trailing slashes and prevent directory traversal
    $path = trim($path, '/');
    $path = str_replace(['../', '..\\'], '', $path);
    return $path;
}

function sendResponse($success, $data = null, $error = null, $code = 200) {
    header('Content-Type: application/json');
    http_response_code($code);
    echo json_encode([
        'success' => $success,
        'data' => $data,
        'error' => $error
    ]);
    exit;
}