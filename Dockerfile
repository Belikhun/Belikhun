# syntax=docker/dockerfile:1

# Copyright (c) 2026 Belikhun. Licensed under the MIT License.
# See LICENSE at the repository root.

# The site as one small image: built with Bun, served by nginx.
#
# harbor builds this from its own copy of the repository, which it cloned once
# and never updates. So the source is not taken from the build context: it is
# fetched from GitHub at build time, and every deploy builds whatever `main` is
# then. To build a local checkout instead:
#
#   docker build --build-arg SOURCE=. -t belikhun-dev .

ARG SOURCE=https://github.com/Belikhun/Belikhun.git#main

FROM oven/bun:1 AS build
ARG SOURCE
WORKDIR /site
ADD ${SOURCE} .
RUN bun install --frozen-lockfile && bun run build

FROM nginx:1.27-alpine
COPY --from=build /site/deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /site/build/ /usr/share/nginx/html/
EXPOSE 80
