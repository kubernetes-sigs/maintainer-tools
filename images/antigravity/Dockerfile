# OCI image bundling the Antigravity CLI (`agy`) and the GitHub CLI (`gh`).
#
# Antigravity install script: https://antigravity.google/cli/install.sh
# It auto-detects platform (linux amd64/arm64, glibc vs musl), verifies a
# SHA512 checksum from the upstream manifest, and drops the `agy` binary into
# $HOME/.local/bin.
#
# `gh` is installed from the official GitHub CLI apt repository so we get
# verified packages and easy multi-arch support.

# Stage 1: run the official Antigravity installer to fetch and verify the binary.
FROM debian:stable-slim AS agy-build

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 agy \
    && useradd -u 1000 -g 1000 --create-home --shell /bin/bash agy
USER agy
WORKDIR /home/agy

# Keep the script on disk rather than piping curl|bash so we get a clean exit
# code and the script is auditable from a running container if needed.
RUN curl -fsSL https://antigravity.google/cli/install.sh -o install.sh \
    && bash install.sh \
    && test -x "$HOME/.local/bin/agy"

# Stage 2: minimal runtime image with both CLIs.
FROM debian:stable-slim

# Install gh and google-cloud-sdk from official apt repos. Follows upstream docs:
# - https://github.com/cli/cli/blob/trunk/docs/install_linux.md
# - https://cloud.google.com/sdk/docs/install#deb
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg git jq \
    && install -dm 755 /etc/apt/keyrings \
    # Install GitHub CLI repository
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    # Install Google Cloud CLI repository
    && echo "deb [signed-by=/etc/apt/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
        > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | gpg --dearmor > /etc/apt/keyrings/cloud.google.gpg \
    # Install both CLIs and yq
    && apt-get update \
    && apt-get install -y --no-install-recommends gh google-cloud-sdk \
    && ARCH="$(dpkg --print-architecture | sed 's/amd64/linux_amd64/;s/arm64/linux_arm64/;s/armhf/linux_arm/')" \
    && curl -fsSL "https://github.com/mikefarah/yq/releases/download/v4.44.1/yq_${ARCH}" -o /usr/local/bin/yq \
    && chmod +x /usr/local/bin/yq \
    && apt-get purge -y --auto-remove gnupg \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 1000 agy \
    && useradd -u 1000 -g 1000 --create-home --shell /bin/bash agy

COPY --from=agy-build /home/agy/.local/bin/agy /usr/local/bin/agy

WORKDIR /workspace
RUN chown agy:agy /workspace

USER agy
# No ENTRYPOINT: both `agy` and `gh` are on PATH, so callers pick the tool.
CMD ["bash"]
