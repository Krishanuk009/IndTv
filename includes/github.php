<?php
require_once __DIR__ . '/../config/config.php';

function githubRequest($endpoint, $method = 'GET', $body = null) {
    $url = "https://api.github.com/repos/" . GITHUB_OWNER . "/" . GITHUB_REPOSITORY . "/" . $endpoint;
    
    $ch = curl_init($url);
    $headers = [
        'Authorization: Bearer ' . GITHUB_TOKEN,
        'User-Agent: PHP-GitHub-Manager',
        'Accept: application/vnd.github+json',
        'X-GitHub-Api-Version: 2022-11-28'
    ];

    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
    
    if ($body) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
        $headers[] = 'Content-Type: application/json';
    }

    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);

    $response = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    return [
        'status' => $status,
        'body' => json_decode($response, true)
    ];
}