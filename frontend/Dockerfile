FROM node:18-alpine

WORKDIR /app

# 安装pnpm
RUN npm install -g pnpm

# 复制package.json和pnpm-lock.yaml
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install

# 复制源代码
COPY . .

# 构建应用
RUN pnpm build

# 安装serve用于生产环境服务静态文件
RUN pnpm install -g serve

EXPOSE 3000

# 使用serve启动构建后的应用
CMD ["serve", "-s", "dist", "-l", "3000"] 