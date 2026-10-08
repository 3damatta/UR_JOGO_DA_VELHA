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

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$action = $_GET['action'] ?? '';
$python_api_url = 'http://127.0.0.1:5000/api';

/**
 * Função utilitária para fazer requisições HTTP para a API Python Flask.
 * Suporta cURL e fallback para stream context com suporte a timeout e ignore_errors.
 */
function proxy_request($url, $method = 'GET', $post_data = null) {
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        if ($method === 'POST') {
            $payload = is_string($post_data) ? $post_data : json_encode($post_data);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
            curl_setopt($ch, CURLOPT_HTTPHEADER, [
                'Content-Type: application/json',
                'Content-Length: ' . strlen($payload)
            ]);
        }
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($response !== false && $http_code > 0) {
            http_response_code($http_code);
            return $response;
        }
    }

    // Fallback: stream context
    $header = "Content-Type: application/json\r\n";
    $content = '';
    if ($method === 'POST') {
        $content = is_string($post_data) ? $post_data : json_encode($post_data);
        $header .= "Content-Length: " . strlen($content) . "\r\n";
    }

    $opts = [
        "http" => [
            "method" => $method,
            "header" => $header,
            "content" => $content,
            "ignore_errors" => true,
            "timeout" => 10
        ]
    ];
    $context = stream_context_create($opts);
    $response = @file_get_contents($url, false, $context);
    return $response;
}

if ($action === 'state') {
    $res = proxy_request("$python_api_url/state", 'GET');
    if ($res === false) {
        http_response_code(502);
        echo json_encode([
            "error" => "Não foi possível conectar ao servidor backend em Python (127.0.0.1:5000).",
            "board" => array_fill(0, 9, ""),
            "game_active" => false,
            "status" => "offline"
        ]);
    } else {
        echo $res;
    }
} elseif ($action === 'reset') {
    $input = file_get_contents('php://input');
    if (!$input) $input = json_encode(new stdClass());
    $res = proxy_request("$python_api_url/reset", 'POST', $input);
    if ($res === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível resetar o jogo no backend."]);
    } else {
        echo $res;
    }
} elseif ($action === 'move') {
    $cell = isset($_GET['cell']) ? (int)$_GET['cell'] : null;
    if ($cell === null) {
        http_response_code(400);
        echo json_encode(["error" => "Célula não informada."]);
        exit;
    }
    $res = proxy_request("$python_api_url/move", 'POST', json_encode(["cell" => $cell]));
    if ($res === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível registrar o movimento no backend."]);
    } else {
        echo $res;
    }
} elseif ($action === 'difficulty') {
    $difficulty = $_GET['difficulty'] ?? 'medium';
    $res = proxy_request("$python_api_url/difficulty", 'POST', json_encode(["difficulty" => $difficulty]));
    if ($res === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível alterar a dificuldade no backend."]);
    } else {
        echo $res;
    }
} elseif ($action === 'positions') {
    $method = $_SERVER['REQUEST_METHOD'];
    $input = ($method === 'POST') ? file_get_contents('php://input') : null;
    $res = proxy_request("$python_api_url/positions", $method, $input);
    if ($res === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível comunicar com o endpoint de posições no backend."]);
    } else {
        echo $res;
    }
} elseif ($action === 'calibrate') {
    $method = $_SERVER['REQUEST_METHOD'];
    $input = ($method === 'POST') ? file_get_contents('php://input') : null;
    $res = proxy_request("$python_api_url/calibrate", $method, $input);
    if ($res === false) {
        http_response_code(502);
        echo json_encode(["error" => "Não foi possível comunicar com o endpoint de calibração no backend."]);
    } else {
        echo $res;
    }
} else {
    http_response_code(400);
    echo json_encode(["error" => "Ação inválida."]);
}
