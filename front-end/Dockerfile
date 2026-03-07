FROM node:20-alpine AS base

# Install bun
RUN npm install -g bun

WORKDIR /app

# Install dependencies
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

# Copy source
COPY . .

EXPOSE 5173

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

# ─── Production Build ────────────────────────────────────────
FROM base AS builder
RUN bun run build

FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .
RUN npm install --omit=dev

EXPOSE 3000
CMD ["node", "build"]
