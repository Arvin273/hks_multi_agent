# =========================
# Stage 1: Build
# =========================
FROM node:20-alpine AS builder

# 安装 pnpm (使用更高效的安装方式)
RUN npm install -g pnpm --no-fund --no-audit

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖并清理缓存
RUN pnpm install --frozen-lockfile && \
    pnpm store prune

# 复制项目源代码
COPY . .

# 构建 Next.js 并清理构建缓存
RUN pnpm build && \
    rm -rf node_modules

# =========================
# Stage 2: Production
# =========================
FROM node:20-alpine AS runner

# 创建非root用户并使用
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# 仅复制生产环境所需文件
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# 更改文件所有权
RUN chown -R nextjs:nodejs /app

USER nextjs

# 暴露端口
EXPOSE 3000

# 使用Node直接启动(更轻量)
CMD ["node", "server.js"]
