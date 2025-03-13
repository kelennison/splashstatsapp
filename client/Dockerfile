# Build stage
FROM node:20-alpine as builder
WORKDIR /app

# Set default API URL (can be overridden via Render's env vars)
ARG REACT_APP_API_URL=https://your-backend.onrender.com
ENV REACT_APP_API_URL=$REACT_APP_API_URL

COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Use Render's PORT (default to 80)
ENV PORT=80
EXPOSE $PORT

CMD ["sh", "-c", "nginx -g 'daemon off;'"]