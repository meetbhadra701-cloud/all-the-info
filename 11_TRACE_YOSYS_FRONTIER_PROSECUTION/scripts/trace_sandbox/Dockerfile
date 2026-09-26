# Hardened runtime for the third-party TRACE binary. Base is the LOCAL alpine:3.20 image (built with --pull=false).
FROM alpine:3.20
COPY trace /opt/trace/trace
RUN chmod 0555 /opt/trace/trace
USER 65534:65534
ENTRYPOINT ["/opt/trace/trace"]
