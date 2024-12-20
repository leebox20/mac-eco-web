# 构建阶段
FROM node:18 AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm config set registry https://registry.npmmirror.com && \
    npm install
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
