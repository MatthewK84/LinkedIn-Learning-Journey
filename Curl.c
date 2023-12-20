#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>

#define BUFFER_SIZE 10000

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <URL>\n", argv[0]);
        return 1;
    }

    char method[10] = "GET";
    char data[BUFFER_SIZE] = "";
    char content_type[100] = "";
    int verbose = 0;

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-v") == 0) {
            verbose = 1;
        } else if (strcmp(argv[i], "-X") == 0 && i + 1 < argc) {
            strncpy(method, argv[++i], sizeof(method) - 1);
        } else if (strcmp(argv[i], "-d") == 0 && i + 1 < argc) {
            strncpy(data, argv[++i], sizeof(data) - 1);
        } else if (strcmp(argv[i], "-H") == 0 && i + 1 < argc) {
            strncpy(content_type, argv[++i], sizeof(content_type) - 1);
        }
    }

    char *url = argv[1];
    char protocol[6], host[100], path[100] = "/";
    int port;

    if (sscanf(url, "%5[^:]://%99[^/]/%99[^\n]", protocol, host, path) != 3) {
        if (sscanf(url, "%5[^:]://%99[^/]", protocol, host) != 2) {
            fprintf(stderr, "Error parsing URL: %s\n", url);
            return 2;
        }
    }

    port = (strcmp(protocol, "https") == 0) ? 443 : 80;

    if (strcmp(protocol, "https") == 0) {
        fprintf(stderr, "HTTPS is not supported in this version.\n");
        return 3;
    }

    struct addrinfo hints, *res;
    int sockfd;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    char port_str[6];
    snprintf(port_str, sizeof(port_str), "%d", port);
    if (getaddrinfo(host, port_str, &hints, &res) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(sockfd));
        return 4;
    }

    sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (sockfd < 0) {
        perror("socket");
        freeaddrinfo(res);
        return 5;
    }

    if (connect(sockfd, res->ai_addr, res->ai_addrlen) < 0) {
        perror("connect");
        close(sockfd);
        freeaddrinfo(res);
        return 6;
    }

    char request[BUFFER_SIZE];
    sprintf(request, "%s %s HTTP/1.1\r\nHost: %s\r\n", method, path, host);
    if (strlen(data) > 0) {
        sprintf(request + strlen(request), "Content-Length: %ld\r\n", strlen(data));
        if (strlen(content_type) > 0) {
            sprintf(request + strlen(request), "Content-Type: %s\r\n", content_type);
        }
    }
    strcat(request, "Connection: close\r\n\r\n");
    if (strlen(data) > 0) {
        strcat(request, data);
    }

    if (verbose) {
        printf("Sending request:\n%s\n", request);
    }

    send(sockfd, request, strlen(request), 0);

    char response[BUFFER_SIZE];
    int received = recv(sockfd, response, BUFFER_SIZE - 1, 0);
    if (received < 0) {
        perror("recv");
        close(sockfd);
        freeaddrinfo(res);
        return 7;
    }

    response[received] = '\0';
    printf("%s", response);

    close(sockfd);
    freeaddrinfo(res);
    return 0;
}