# Builds the ListRiver MCP server (mcp/) from the source in this repository and runs it over stdio.
#   docker build -t listriver-mcp .
#   docker run -i --rm -e LISTRIVER_API_KEY=lr_key_... listriver-mcp
FROM python:3.12-slim
WORKDIR /app
COPY python/ /app/python/
COPY mcp/ /app/mcp/
RUN pip install --no-cache-dir /app/python /app/mcp
CMD ["listriver-mcp"]
