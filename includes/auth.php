<?php
require_once __DIR__ . '/session.php';

function isAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

function requireAuth() {
    if (!isAuthenticated()) {
        if (strpos($_SERVER['REQUEST_URI'], '/api/') !== false) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Unauthorized']);
            exit;
        }
        header('Location: login.php');
        exit;
    }
}