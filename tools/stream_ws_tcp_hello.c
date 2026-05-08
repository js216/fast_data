// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Jakob Kastelic

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

static int write_all(int fd, const char *buf, size_t len)
{
    while (len > 0) {
        ssize_t written = write(fd, buf, len);
        if (written < 0) {
            if (errno == EINTR)
                continue;
            return -1;
        }
        if (written == 0)
            return -1;
        buf += written;
        len -= (size_t)written;
    }

    return 0;
}

int main(void)
{
    static const char reply[] = "stream_ws_tcp_hello\n";
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0)
        return 1;

    int reuse = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &reuse,
                   sizeof(reuse)) < 0) {
        close(server_fd);
        return 1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(8765);

    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 1) < 0) {
        close(server_fd);
        return 1;
    }

    int client_fd;
    do {
        client_fd = accept(server_fd, NULL, NULL);
    } while (client_fd < 0 && errno == EINTR);

    if (client_fd < 0) {
        close(server_fd);
        return 1;
    }

    int rc = write_all(client_fd, reply, sizeof(reply) - 1);
    close(client_fd);
    close(server_fd);

    return rc == 0 ? 0 : 1;
}
