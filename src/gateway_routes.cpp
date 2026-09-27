/**
 * Tantric AI Agent - HTTP/WebSocket Gateway Implementation
 *
 * Non-blocking (epoll) HTTP/1.1 + RFC 6455 WebSocket gateway.
 * Zero external dependencies: SHA-1 + base64 implemented inline.
 */

#include "gateway_routes.hpp"
#include "gateway_security.hpp"

#include <arpa/inet.h>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#include <algorithm>
#include <array>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <vector>

namespace tantric::gateway {

// ============================================
// SHA-1 (RFC 3174) — for the WebSocket handshake only
// ============================================
namespace {

struct Sha1 {
    uint32_t h[5] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0};
    uint64_t total = 0;
    uint8_t buf[64];
    size_t buflen = 0;

    static uint32_t rol(uint32_t x, int n) { return (x << n) | (x >> (32 - n)); }

    void process(const uint8_t* p) {
        uint32_t w[80];
        for (int i = 0; i < 16; ++i)
            w[i] = (uint32_t(p[i * 4]) << 24) | (uint32_t(p[i * 4 + 1]) << 16) |
                   (uint32_t(p[i * 4 + 2]) << 8) | uint32_t(p[i * 4 + 3]);
        for (int i = 16; i < 80; ++i)
            w[i] = rol(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);

        uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4];
        for (int i = 0; i < 80; ++i) {
            uint32_t f, k;
            if (i < 20)      { f = (b & c) | ((~b) & d);        k = 0x5A827999; }
            else if (i < 40) { f = b ^ c ^ d;                   k = 0x6ED9EBA1; }
            else if (i < 60) { f = (b & c) | (b & d) | (c & d); k = 0x8F1BBCDC; }
            else             { f = b ^ c ^ d;                   k = 0xCA62C1D6; }
            uint32_t tmp = rol(a, 5) + f + e + k + w[i];
            e = d; d = c; c = rol(b, 30); b = a; a = tmp;
        }
        h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e;
    }

    void update(const uint8_t* p, size_t n) {
        total += n;
        while (n) {
            size_t take = std::min(n, size_t(64) - buflen);
            std::memcpy(buf + buflen, p, take);
            buflen += take; p += take; n -= take;
            if (buflen == 64) { process(buf); buflen = 0; }
        }
    }

    std::array<uint8_t, 20> final() {
        uint64_t bits = total * 8;
        uint8_t pad = 0x80, zero = 0x00;
        update(&pad, 1);
        while (buflen != 56) update(&zero, 1);
        uint8_t lenb[8];
        for (int i = 0; i < 8; ++i) lenb[i] = uint8_t((bits >> (56 - 8 * i)) & 0xFF);
        update(lenb, 8);

        std::array<uint8_t, 20> out;
        for (int i = 0; i < 5; ++i) {
            out[i * 4]     = uint8_t(h[i] >> 24);
            out[i * 4 + 1] = uint8_t(h[i] >> 16);
            out[i * 4 + 2] = uint8_t(h[i] >> 8);
            out[i * 4 + 3] = uint8_t(h[i]);
        }
        return out;
    }
};

std::array<uint8_t, 20> sha1(const std::string& s) {
    Sha1 ctx;
    ctx.update(reinterpret_cast<const uint8_t*>(s.data()), s.size());
    return ctx.final();
}

// ============================================
// IPC: length-prefixed JSON over Unix Domain Socket
// ============================================
std::string ipc_call(const std::string& sock_path, const std::string& req_json) {
    int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) return "";

    timeval tv{};
    tv.tv_sec = 5;
    ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    ::setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    sockaddr_un sa{};
    sa.sun_family = AF_UNIX;
    std::strncpy(sa.sun_path, sock_path.c_str(), sizeof(sa.sun_path) - 1);

    if (::connect(fd, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) != 0) {
        ::close(fd);
        return "";
    }

    auto send_all = [&](const char* p, size_t n) -> bool {
        while (n) {
            ssize_t w = ::send(fd, p, n, MSG_NOSIGNAL);
            if (w <= 0) return false;
            p += w; n -= size_t(w);
        }
        return true;
    };
    auto recv_exact = [&](char* p, size_t n) -> bool {
        while (n) {
            ssize_t r = ::recv(fd, p, n, 0);
            if (r <= 0) return false;
            p += r; n -= size_t(r);
        }
        return true;
    };

    uint32_t len = uint32_t(req_json.size());
    char hdr[4] = {char(len & 0xFF), char((len >> 8) & 0xFF),
                   char((len >> 16) & 0xFF), char((len >> 24) & 0xFF)};
    bool ok = send_all(hdr, 4) && send_all(req_json.data(), req_json.size());

    std::string resp;
    if (ok) {
        char rh[4];
        if (recv_exact(rh, 4)) {
            uint32_t rlen = uint32_t(uint8_t(rh[0])) | (uint32_t(uint8_t(rh[1])) << 8) |
                            (uint32_t(uint8_t(rh[2])) << 16) | (uint32_t(uint8_t(rh[3])) << 24);
            if (rlen > 0 && rlen < 8 * 1024 * 1024) {
                resp.resize(rlen);
                if (!recv_exact(resp.data(), rlen)) resp.clear();
            }
        }
    }
    ::close(fd);
    return resp;
}

std::string json_escape(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 8);
    for (char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (uint8_t(c) < 0x20) {
                    char b[8];
                    std::snprintf(b, sizeof(b), "\\u%04x", uint8_t(c));
                    out += b;
                } else out += c;
        }
    }
    return out;
}

} // anonymous namespace

// ============================================
// Static helpers (exposed for tests)
// ============================================
std::string HttpGateway::base64_encode(const uint8_t* data, size_t len) {
    static const char tbl[] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string out;
    out.reserve(((len + 2) / 3) * 4);
    for (size_t i = 0; i < len; i += 3) {
        uint32_t v = uint32_t(data[i]) << 16;
        bool b1 = i + 1 < len, b2 = i + 2 < len;
        if (b1) v |= uint32_t(data[i + 1]) << 8;
        if (b2) v |= uint32_t(data[i + 2]);
        out += tbl[(v >> 18) & 63];
        out += tbl[(v >> 12) & 63];
        out += b1 ? tbl[(v >> 6) & 63] : '=';
        out += b2 ? tbl[v & 63] : '=';
    }
    return out;
}

std::string HttpGateway::ws_accept_key(const std::string& sec_ws_key) {
    static const char* GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
    auto digest = sha1(sec_ws_key + GUID);
    return base64_encode(digest.data(), digest.size());
}

std::string HttpGateway::json_extract_string(const std::string& json,
                                             const std::string& key) {
    std::string needle = "\"" + key + "\"";
    auto kpos = json.find(needle);
    if (kpos == std::string::npos) return "";
    auto colon = json.find(':', kpos + needle.size());
    if (colon == std::string::npos) return "";
    auto q1 = json.find('"', colon + 1);
    if (q1 == std::string::npos) return "";

    std::string out;
    for (size_t i = q1 + 1; i < json.size(); ++i) {
        char c = json[i];
        if (c == '\\' && i + 1 < json.size()) {
            char nxt = json[i + 1];
            if (nxt == 'n') out += '\n';
            else if (nxt == 't') out += '\t';
            else if (nxt == 'r') out += '\r';
            else out += nxt;
            ++i;
        } else if (c == '"') {
            return out;
        } else {
            out += c;
        }
    }
    return "";
}

std::string HttpGateway::url_decode(const std::string& s) {
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '%' && i + 2 < s.size()) {
            auto hex = [](char c) -> int {
                if (c >= '0' && c <= '9') return c - '0';
                if (c >= 'a' && c <= 'f') return c - 'a' + 10;
                if (c >= 'A' && c <= 'F') return c - 'A' + 10;
                return -1;
            };
            int hi = hex(s[i + 1]), lo = hex(s[i + 2]);
            if (hi >= 0 && lo >= 0) {
                out += char((hi << 4) | lo);
                i += 2;
                continue;
            }
        } else if (s[i] == '+') {
            out += ' ';
            continue;
        }
        out += s[i];
    }
    return out;
}

// ============================================
// Connection state
// ============================================
namespace {

struct HttpReq {
    std::string method, target, path, query, version;
    std::unordered_map<std::string, std::string> headers;
};

struct WsFrame {
    bool fin = true;
    uint8_t opcode = 0;
    std::string payload;
};

struct Conn {
    int fd = -1;
    std::string in, out;
    size_t out_off = 0;
    bool ws = false;
    bool close_after_flush = false;
    WsFrameLimiter fps;
    std::string frag;
    int frag_op = -1;
    std::string session_user;
};

void set_nonblocking(int fd) {
    int fl = ::fcntl(fd, F_GETFL, 0);
    ::fcntl(fd, F_SETFL, fl | O_NONBLOCK);
}

bool parse_http_request(const std::string& head, HttpReq& r) {
    std::istringstream ss(head);
    std::string line;
    if (!std::getline(ss, line)) return false;
    if (!line.empty() && line.back() == '\r') line.pop_back();

    std::istringstream lss(line);
    if (!(lss >> r.method >> r.target >> r.version)) return false;

    auto qpos = r.target.find('?');
    if (qpos == std::string::npos) {
        r.path = r.target;
    } else {
        r.path = r.target.substr(0, qpos);
        r.query = r.target.substr(qpos + 1);
    }

    while (std::getline(ss, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) break;
        auto c = line.find(':');
        if (c == std::string::npos) continue;
        std::string k = line.substr(0, c);
        std::string v = line.substr(c + 1);
        std::transform(k.begin(), k.end(), k.begin(), ::tolower);
        size_t s = v.find_first_not_of(" \t");
        if (s != std::string::npos) v = v.substr(s);
        r.headers[k] = v;
    }
    return true;
}

bool next_ws_frame(std::string& buf, WsFrame& f) {
    if (buf.size() < 2) return false;
    const uint8_t* p = reinterpret_cast<const uint8_t*>(buf.data());
    bool fin = (p[0] & 0x80) != 0;
    uint8_t op = p[0] & 0x0F;
    bool masked = (p[1] & 0x80) != 0;
    uint64_t len = p[1] & 0x7F;
    size_t hdr = 2;

    if (len == 126) {
        if (buf.size() < 4) return false;
        len = (uint64_t(p[2]) << 8) | p[3];
        hdr = 4;
    } else if (len == 127) {
        if (buf.size() < 10) return false;
        len = 0;
        for (int i = 0; i < 8; ++i) len = (len << 8) | p[2 + i];
        hdr = 10;
    }
    if (len > 4 * 1024 * 1024) return false;      // protocol limit
    if (masked) hdr += 4;
    if (buf.size() < hdr + len) return false;

    std::string payload(reinterpret_cast<const char*>(p) + hdr, size_t(len));
    if (masked) {
        const uint8_t* m = p + hdr - 4;
        for (size_t i = 0; i < payload.size(); ++i)
            payload[i] = char(uint8_t(payload[i]) ^ m[i & 3]);
    }
    buf.erase(0, hdr + size_t(len));
    f.fin = fin;
    f.opcode = op;
    f.payload = std::move(payload);
    return true;
}

void ws_send(Conn& c, uint8_t opcode, const std::string& payload) {
    std::string fr;
    fr += char(0x80 | opcode);
    size_t n = payload.size();
    if (n < 126) {
        fr += char(n);
    } else if (n < 65536) {
        fr += char(126);
        fr += char((n >> 8) & 0xFF);
        fr += char(n & 0xFF);
    } else {
        fr += char(127);
        for (int i = 7; i >= 0; --i) fr += char((uint64_t(n) >> (8 * i)) & 0xFF);
    }
    fr += payload;
    c.out += fr;
}

} // anonymous namespace

// ============================================
// Gateway implementation
// ============================================
struct HttpGateway::Impl {
    std::unordered_map<int, Conn*> conns;
    ~Impl() {
        for (auto& [fd, c] : conns) { ::close(fd); delete c; }
    }
};

HttpGateway::HttpGateway(GatewayConfig cfg) : cfg_(std::move(cfg)) {
    impl_ = new Impl();
}

HttpGateway::~HttpGateway() {
    if (listen_fd_ >= 0) ::close(listen_fd_);
    if (epoll_fd_ >= 0) ::close(epoll_fd_);
    delete impl_;
}

bool HttpGateway::start() {
    listen_fd_ = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd_ < 0) return false;

    int one = 1;
    ::setsockopt(listen_fd_, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    set_nonblocking(listen_fd_);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(cfg_.port);

    if (::bind(listen_fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0)
        return false;
    if (::listen(listen_fd_, 128) != 0) return false;

    epoll_fd_ = ::epoll_create1(0);
    if (epoll_fd_ < 0) return false;

    epoll_event ev{};
    ev.events = EPOLLIN;
    ev.data.fd = listen_fd_;
    ::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, listen_fd_, &ev);

    std::fprintf(stderr, "[GATEWAY] listening on :%u (static=%s ipc=%s)\n",
                 cfg_.port, cfg_.static_root.c_str(), cfg_.ipc_socket.c_str());
    return true;
}

namespace {

void conn_update_events(int epoll_fd, Conn* c) {
    epoll_event ev{};
    ev.events = EPOLLIN | (c->out.empty() ? 0u : EPOLLOUT);
    ev.data.fd = c->fd;
    ::epoll_ctl(epoll_fd, EPOLL_CTL_MOD, c->fd, &ev);
}

void conn_queue_write(Conn* c, const std::string& data) { c->out += data; }

void http_response(Conn* c, int status, const std::string& reason,
                   const std::string& body,
                   const std::string& ctype = "application/json") {
    std::string head =
        "HTTP/1.1 " + std::to_string(status) + " " + reason + "\r\n" +
        "Content-Type: " + ctype + "\r\n" +
        "Content-Length: " + std::to_string(body.size()) + "\r\n" +
        "Access-Control-Allow-Origin: *\r\n" +
        "Connection: close\r\n\r\n";
    conn_queue_write(c, head + body);
    c->close_after_flush = true;
}

std::string read_file(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) return "";
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

bool validate_via_ipc(const std::string& sock, const std::string& token,
                      const std::string& client_id, std::string& user_id) {
    std::string req = "{\"action\": \"VALIDATE_SESSION\", \"token\": \"" +
                      json_escape(token) + "\"}";
    std::string resp = ipc_call(sock, req);
    if (resp.find("\"SUCCESS\"") == std::string::npos) return false;
    user_id = HttpGateway::json_extract_string(resp, "user_id");
    (void)client_id;
    return true;
}

std::string query_param(const std::string& query, const std::string& key) {
    size_t pos = 0;
    while (pos < query.size()) {
        auto amp = query.find('&', pos);
        std::string pair = query.substr(pos, amp == std::string::npos
                                               ? std::string::npos : amp - pos);
        auto eq = pair.find('=');
        if (eq != std::string::npos) {
            if (pair.substr(0, eq) == key)
                return HttpGateway::url_decode(pair.substr(eq + 1));
        }
        if (amp == std::string::npos) break;
        pos = amp + 1;
    }
    return "";
}

} // anonymous namespace

int HttpGateway::run() {
    running_ = true;
    constexpr int MAX_EVENTS = 64;
    epoll_event events[MAX_EVENTS];

    while (running_) {
        int n = ::epoll_wait(epoll_fd_, events, MAX_EVENTS, 1000);
        if (n < 0) {
            if (errno == EINTR) continue;
            break;
        }

        for (int i = 0; i < n; ++i) {
            int fd = events[i].data.fd;

            // ---------- accept ----------
            if (fd == listen_fd_) {
                for (;;) {
                    sockaddr_in peer{};
                    socklen_t plen = sizeof(peer);
                    int cfd = ::accept4(listen_fd_, reinterpret_cast<sockaddr*>(&peer),
                                        &plen, SOCK_NONBLOCK);
                    if (cfd < 0) break;
                    int one = 1;
                    ::setsockopt(cfd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one));

                    auto* c = new Conn();
                    c->fd = cfd;
                    impl_->conns[cfd] = c;

                    epoll_event ev{};
                    ev.events = EPOLLIN;
                    ev.data.fd = cfd;
                    ::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, cfd, &ev);
                }
                continue;
            }

            auto it = impl_->conns.find(fd);
            if (it == impl_->conns.end()) continue;
            Conn* c = it->second;

            bool dead = false;

            // ---------- read ----------
            if (events[i].events & (EPOLLIN | EPOLLHUP | EPOLLERR)) {
                char buf[65536];
                for (;;) {
                    ssize_t r = ::recv(fd, buf, sizeof(buf), 0);
                    if (r > 0) {
                        c->in.append(buf, size_t(r));
                        continue;
                    }
                    if (r == 0) { dead = true; break; }
                    if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                    dead = true;
                    break;
                }
            }

            // ---------- process ----------
            if (!dead) {
                for (;;) {
                    if (!c->ws) {
                        auto pos = c->in.find("\r\n\r\n");
                        if (pos == std::string::npos) break;
                        std::string head = c->in.substr(0, pos);
                        HttpReq r;
                        if (!parse_http_request(head, r)) {
                            http_response(c, 400, "Bad Request", "{\"status\":\"ERROR\"}");
                            break;
                        }

                        size_t clen = 0;
                        auto cl = r.headers.find("content-length");
                        if (cl != r.headers.end()) {
                            try { clen = std::stoul(cl->second); } catch (...) { clen = 0; }
                        }
                        if (c->in.size() < pos + 4 + clen) break;   // wait for body
                        std::string body = c->in.substr(pos + 4, clen);
                        c->in.erase(0, pos + 4 + clen);

                        // ======== ROUTES ========
                        const std::string& m = r.method;
                        const std::string& p = r.path;

                        if (m == "GET" && p == "/healthz") {
                            http_response(c, 200, "OK",
                                "{\"status\":\"ok\",\"service\":\"tantric-gateway\"}");
                        } else if (m == "GET" && (p == "/" || p == "/index.html")) {
                            std::string html = read_file(cfg_.static_root + "/index.html");
                            if (html.empty())
                                http_response(c, 404, "Not Found", "web/index.html missing");
                            else
                                http_response(c, 200, "OK", html, "text/html; charset=utf-8");
                        } else if (m == "GET" && p == "/v1/auth/config") {
                            std::string j = "{\"status\":\"SUCCESS\",\"client_id\":\"" +
                                            json_escape(cfg_.client_id) +
                                            "\",\"enabled\":" +
                                            (cfg_.client_id.empty() ? "false" : "true") +
                                            "}";
                            http_response(c, 200, "OK", j);
                        } else if (m == "POST" && p == "/api/v1/auth/google") {
                            std::string id_token = json_extract_string(body, "id_token");
                            if (id_token.empty()) {
                                http_response(c, 400, "Bad Request",
                                    "{\"status\":\"ERROR\",\"message\":\"missing id_token\"}");
                            } else {
                                std::string req =
                                    "{\"action\": \"VERIFY_GOOGLE_OAUTH\", \"id_token\": \"" +
                                    json_escape(id_token) + "\"}";
                                std::string resp = ipc_call(cfg_.ipc_socket, req);
                                if (resp.empty())
                                    http_response(c, 502, "Bad Gateway",
                                        "{\"status\":\"ERROR\",\"message\":\"auth service unavailable\"}");
                                else
                                    http_response(c, 200, "OK", resp);
                            }
                        } else if (m == "GET" && p == "/v1/chat/ws") {
                            std::string token = query_param(r.query, "token");
                            if (token.empty()) {
                                auto proto = r.headers.find("sec-websocket-protocol");
                                if (proto != r.headers.end()) token = proto->second;
                            }
                            std::string user_id;
                            if (token.empty() ||
                                !validate_via_ipc(cfg_.ipc_socket, token, cfg_.client_id, user_id)) {
                                http_response(c, 401, "Unauthorized",
                                    "{\"status\":\"ERROR\",\"message\":\"invalid session\"}");
                            } else {
                                auto keyit = r.headers.find("sec-websocket-key");
                                if (keyit == r.headers.end()) {
                                    http_response(c, 400, "Bad Request",
                                        "{\"status\":\"ERROR\",\"message\":\"missing Sec-WebSocket-Key\"}");
                                } else {
                                    std::string accept = ws_accept_key(keyit->second);
                                    std::string head101 =
                                        "HTTP/1.1 101 Switching Protocols\r\n"
                                        "Upgrade: websocket\r\n"
                                        "Connection: Upgrade\r\n"
                                        "Sec-WebSocket-Accept: " + accept + "\r\n\r\n";
                                    conn_queue_write(c, head101);
                                    c->ws = true;
                                    c->session_user = user_id;
                                    std::fprintf(stderr, "[GATEWAY] WS upgraded user=%s\n",
                                                 user_id.c_str());
                                }
                            }
                        } else {
                            http_response(c, 404, "Not Found",
                                "{\"status\":\"ERROR\",\"message\":\"no route\"}");
                        }
                        // ======== end routes ========

                        if (!c->ws) break;       // response queued; flush & close
                    }

                    // ---------- websocket frames ----------
                    if (c->ws) {
                        WsFrame f;
                        if (!next_ws_frame(c->in, f)) break;

                        if (f.opcode == 0x8) {              // close
                            ws_send(*c, 0x8, "");
                            c->close_after_flush = true;
                            break;
                        }
                        if (f.opcode == 0x9) {              // ping -> pong
                            ws_send(*c, 0xA, f.payload);
                            conn_update_events(epoll_fd_, c);
                            continue;
                        }
                        if (f.opcode == 0xA) continue;      // pong: ignore

                        if (!c->fps.allow_frame()) {        // rate limit (20 fps)
                            ws_send(*c, 0x1,
                                "{\"type\":\"error\",\"code\":\"RATE_LIMIT\","
                                "\"message\":\"frame budget exceeded (20 fps max)\"}");
                            c->close_after_flush = true;
                            std::fprintf(stderr, "[GATEWAY] WS rate limit hit fd=%d\n", fd);
                            break;
                        }

                        if (f.opcode == 0x1 || f.opcode == 0x0) {
                            if (!f.fin) {
                                c->frag += f.payload;
                                if (c->frag_op < 0) c->frag_op = 1;
                                continue;
                            }
                            std::string full = c->frag + f.payload;
                            c->frag.clear();
                            c->frag_op = -1;

                            std::string content = json_extract_string(full, "content");
                            std::string reply =
                                "{\"type\":\"diagnostic_chunk\",\"section\":\"diagnostic\","
                                "\"content\":\"[ack] " + json_escape(content) + "\","
                                "\"final\":true}";
                            ws_send(*c, 0x1, reply);
                        } else {
                            ws_send(*c, 0x1,
                                "{\"type\":\"error\",\"code\":\"UNSUPPORTED_OPCODE\"}");
                        }
                        conn_update_events(epoll_fd_, c);
                        continue;
                    }
                    break;
                }
            }

            // ---------- write ----------
            if (!dead && !c->out.empty()) {
                while (c->out_off < c->out.size()) {
                    ssize_t w = ::send(fd, c->out.data() + c->out_off,
                                       c->out.size() - c->out_off, MSG_NOSIGNAL);
                    if (w > 0) { c->out_off += size_t(w); continue; }
                    if (w < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) break;
                    dead = true;
                    break;
                }
                if (c->out_off >= c->out.size()) {
                    c->out.clear();
                    c->out_off = 0;
                    if (c->close_after_flush) dead = true;
                }
            }

            if (dead || (c->close_after_flush && c->out.empty())) {
                ::epoll_ctl(epoll_fd_, EPOLL_CTL_DEL, fd, nullptr);
                ::close(fd);
                delete c;
                impl_->conns.erase(fd);
            } else {
                conn_update_events(epoll_fd_, c);
            }
        }
    }
    return 0;
}

} // namespace tantric::gateway
