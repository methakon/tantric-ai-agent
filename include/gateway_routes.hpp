/**
 * Tantric AI Agent - HTTP/WebSocket Gateway
 *
 * Non-blocking epoll HTTP/1.1 server implementing:
 *   POST /api/v1/auth/google   -> VERIFY_GOOGLE_OAUTH over UDS to ipc_bridge.py
 *   GET  /v1/auth/config       -> public client-id config for GIS
 *   GET  /v1/chat/ws?token=... -> RFC 6455 upgrade + frame loop (20 fps cap)
 *   GET  /                     -> web/index.html
 *   GET  /healthz              -> liveness
 *
 * Session validation for the WebSocket handshake is delegated to the
 * Python auth service (single source of truth) via VALIDATE_SESSION.
 */

#pragma once

#include <cstdint>
#include <string>

namespace tantric::gateway {

struct GatewayConfig {
    uint16_t port = 8080;
    std::string static_root = "web";
    std::string ipc_socket = "/tmp/hermes_esoteric.sock";
    std::string client_id;              // GOOGLE_CLIENT_ID (may be empty)
};

class HttpGateway {
public:
    explicit HttpGateway(GatewayConfig cfg);
    ~HttpGateway();

    HttpGateway(const HttpGateway&) = delete;
    HttpGateway& operator=(const HttpGateway&) = delete;

    bool start();
    int run();
    void request_stop() { running_ = false; }

    // Exposed for unit tests
    static std::string ws_accept_key(const std::string& sec_ws_key);
    static std::string base64_encode(const uint8_t* data, size_t len);
    static std::string json_extract_string(const std::string& json, const std::string& key);
    static std::string url_decode(const std::string& s);

private:
    GatewayConfig cfg_;
    int listen_fd_ = -1;
    int epoll_fd_ = -1;
    bool running_ = false;

    struct Impl;                        // connection state
    Impl* impl_ = nullptr;
};

} // namespace tantric::gateway
