FROM node:18-alpine

WORKDIR /app

# Install dependencies for building
COPY package*.json ./

# Clean install with all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
