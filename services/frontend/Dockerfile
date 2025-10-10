FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_ORCHESTRATOR_URL=http://localhost:8003
ARG VITE_ASR_URL=http://localhost:8004
ARG VITE_TTS_URL=http://localhost:8005
ARG VITE_TOOLSERVER_URL=http://localhost:8002

ENV VITE_ORCHESTRATOR_URL=$VITE_ORCHESTRATOR_URL
ENV VITE_ASR_URL=$VITE_ASR_URL
ENV VITE_TTS_URL=$VITE_TTS_URL
ENV VITE_TOOLSERVER_URL=$VITE_TOOLSERVER_URL

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
