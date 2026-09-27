/**
 * Tantric AI Agent - Gateway Entry Point
 *
 * Loads configuration from .env (project root) + environment, then runs
 * the non-blocking HTTP/WebSocket gateway.
 *
 * Usage:
 *   ./tantric_gateway              # start gateway (default :8080)
 *   ./tantric_gateway --port 9090  # override port
 */

#include "gateway_routes.hpp"

#include <csignal>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>

namespace {

std::unordered_map<std::string, std::string> g_env;

void load_dotenv() {
    const char* candidates[] = {".env", "../.env", "../../.env"};
    for (const char* path : candidates) {
        std::ifstream f(path);
        if (!f) continue;
        std::string line;
        while (std::getline(f, line)) {
            if (line.empty() || line[0] == '#') continue;
            auto eq = line.find('=');
            if (eq == std::string::npos) continue;
            std::string k = line.substr(0, eq);
            std::string v = line.substr(eq + 1);
            while (!k.empty() && (k.back() == ' ' || k.back() == '\t')) k.pop_back();
            while (!v.empty() && (v.back() == '\r' || v.back() == '\n')) v.pop_back();
            g_env[k] = v;
        }
        break;
    }
}

std::string env_or(const std::string& key, const std::string& fallback) {
    const char* v = std::getenv(key.c_str());
    if (v && *v) return v;
    auto it = g_env.find(key);
    if (it != g_env.end() && !it->second.empty()) return it->second;
    return fallback;
}

tantric::gateway::HttpGateway* g_gateway = nullptr;

void on_signal(int) {
    if (g_gateway) g_gateway->request_stop();
}

} // anonymous namespace

int main(int argc, char** argv) {
    std::signal(SIGPIPE, SIG_IGN);
    load_dotenv();

    tantric::gateway::GatewayConfig cfg;
    cfg.port = static_cast<uint16_t>(std::stoi(env_or("GATEWAY_PORT", "8080")));
    cfg.static_root = env_or("WEB_ROOT", "web");
    cfg.ipc_socket = env_or("ESOTERIC_SOCKET_PATH", "/tmp/hermes_esoteric.sock");
    cfg.client_id = env_or("GOOGLE_CLIENT_ID", "");

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--port" && i + 1 < argc) {
            cfg.port = static_cast<uint16_t>(std::stoi(argv[++i]));
        }
    }

    std::cout << "=== Tantric AI Agent Gateway ===\n";
    std::cout << "Port:        " << cfg.port << "\n";
    std::cout << "Static root: " << cfg.static_root << "\n";
    std::cout << "IPC socket:  " << cfg.ipc_socket << "\n";
    std::cout << "Google OAuth: " << (cfg.client_id.empty() ? "NOT CONFIGURED" : "configured") << "\n";
    std::cout << std::flush;

    tantric::gateway::HttpGateway gw(std::move(cfg));
    g_gateway = &gw;

    std::signal(SIGINT, on_signal);
    std::signal(SIGTERM, on_signal);

    if (!gw.start()) {
        std::cerr << "[FATAL] failed to bind gateway socket\n";
        return 1;
    }

    std::cout << "[GATEWAY] ready — routes:\n"
              << "  POST /api/v1/auth/google\n"
              << "  GET  /v1/auth/config\n"
              << "  GET  /v1/chat/ws?token=...\n"
              << "  GET  /healthz\n" << std::flush;

    return gw.run();
}
