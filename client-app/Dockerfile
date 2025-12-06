## Client App - Vue 3 + Vite (LuxeTrade)
## Multi-stage build: Node (build) -> Nginx (serve static)

FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration and remove default config
COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
