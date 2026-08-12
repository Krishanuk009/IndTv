<?php
require_once 'includes/auth.php';
header('Location: ' . (isAuthenticated() ? 'dashboard.php' : 'login.php'));
exit;