#!/bin/bash
docker build -f Dockerfile.server -t news-stories-expr-server:latest .
docker run -d -p 11111:5000 -v /data/anwala/IMLS/StoryGraph/graphs:/usr/src/app/static/graphs -v /data/anwala/IMLS/StoryGraph/graph-cursors:/usr/src/app/graphs -v /data/anwala/IMLS/StoryGraph/generic:/usr/src/app/generic news-stories-expr-server