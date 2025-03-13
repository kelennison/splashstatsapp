# Build stage
FROM node:22.14-alpine3.21 as builder

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    libc6-compat \
    libpng-dev \
    pango-dev \
    cairo-dev \
    jpeg-dev \
    giflib-dev

# Install npm packages
WORKDIR /app
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Copy source files (excluding .env if missing)
COPY public/ public/
COPY src/ src/
COPY .env* ./  

# Build the app
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:5000}
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]