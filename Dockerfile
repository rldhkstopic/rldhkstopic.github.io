FROM ruby:3.3-slim

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY Gemfile Gemfile.lock* ./
RUN gem install bundler && \
    bundle config set --local path 'vendor/bundle' && \
    bundle install

COPY . .
# 엔트리포인트를 이미지 내부에 생성 (CRLF 이슈 방지)
RUN printf '%s\n' '#!/bin/sh' 'set -e' 'bundle config set --local path vendor/bundle' 'bundle install' 'exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 4000 35729

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--port", "4000", "--livereload", "--force_polling"]
