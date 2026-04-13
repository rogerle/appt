# Appt Frontend - Vue 3 + Vite Docker Image
# Stage 1: Development stage (for hot reload during development)
FROM node:20-alpine as development

WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install production dependencies only
RUN npm install --omit=dev

# Copy source code
COPY . .

# Expose dev server port
EXPOSE 5173

# Start development server with hot reload
CMD ["npm", "run", "dev", "--", "--host"]

# ============================================================================
# Stage 2: Production build stage
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install all dependencies (including devDependencies for build)
RUN npm install

# Copy source code
COPY . .

# Build production bundle
RUN npm run build

# ============================================================================
# Stage 3: Production stage with nginx
FROM nginx:alpine as production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
