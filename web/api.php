<?php
/**
 * Proxy API em PHP para o Backend Python Flask
 * ============================================
 * Encaminha chamadas AJAX do frontend para o orquestrador em Python.
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

$action = $_GET['action'] ?? '';
$python_api_url = 'http://localhost:5000/api';

if ($action === 'state') {
    $response = @file_get_contents("$python_api_url/state");
    if ($response === false) {
        http_response_code(502);
        echo json_encode([
            "error" => "Não foi possível conectar ao servidor backend em Python.",
            "board" => array_fill(0, 9, ""),
            "game_active" => false,
            "status" => "offline"
        ]);
    } else {
        echo $response;
    }
} elseif ($action === 'reset') {
    $data = json_encode(new stdClass());
    $opts = [
        "http" => [
            "method" => "POST",
            "header" => "Content-Type: application/json\r\nContent-Length: " . strlen($data) . "\r\n",
            "content" => $data
        ]
    ];
    $context = stream_context_create($opts);
    $response = @file_get_contents("$python_api_url/reset", false, $context);
    if ($response === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível resetar o jogo no backend."]);
    } else {
        echo $response;
    }
} elseif ($action === 'move') {
    $cell = isset($_GET['cell']) ? (int)$_GET['cell'] : null;
    if ($cell === null) {
        http_response_code(400);
        echo json_encode(["error" => "Célula não informada."]);
        exit;
    }

    $data = json_encode(["cell" => $cell]);
    $opts = [
        "http" => [
            "method" => "POST",
            "header" => "Content-Type: application/json\r\nContent-Length: " . strlen($data) . "\r\n",
            "content" => $data
        ]
    ];
    $context = stream_context_create($opts);
    $response = @file_get_contents("$python_api_url/move", false, $context);
    if ($response === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível registrar o movimento no backend."]);
    } else {
        echo $response;
    }
} elseif ($action === 'difficulty') {
    $difficulty = $_GET['difficulty'] ?? 'medium';
    $data = json_encode(["difficulty" => $difficulty]);
    $opts = [
        "http" => [
            "method" => "POST",
            "header" => "Content-Type: application/json\r\nContent-Length: " . strlen($data) . "\r\n",
            "content" => $data
        ]
    ];
    $context = stream_context_create($opts);
    $response = @file_get_contents("$python_api_url/difficulty", false, $context);
    if ($response === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível alterar a dificuldade no backend."]);
    } else {
        echo $response;
    }
} else {
    http_response_code(400);
    echo json_encode(["error" => "Ação inválida."]);
}
