# Insurance Management System - Docker Setup

This project provides a complete Docker Compose setup for the Insurance Management System with microservices architecture.

## 🏗️ Architecture

- **Frontend**: Angular 16 application (Port 4200)
- **Gateway**: API Gateway with authentication (Port 5000)
- **Policy Service**: Policy management microservice (Port 5001)
- **Claim Service**: Claims processing microservice (Port 5002)

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10 or later
- Docker Compose 2.0 or later

### Development Mode

```bash
# Start in development mode with hot reloading
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

## 📋 Available Commands

### Basic Operations

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Rebuild specific service
docker-compose build gateway
docker-compose up -d gateway

# Access container shell
docker-compose exec gateway bash
docker-compose exec frontend sh
```

### Data Management

```bash
# Remove all data volumes (CAUTION: This deletes all data)
docker-compose down -v

# Backup database
docker cp ims-gateway:/app/instance ./backup/

# View volume information
docker volume ls
docker volume inspect main_gateway-data
```

## 🌐 Service URLs

Once started, the services will be available at:

- **Frontend**: http://localhost:4200
- **API Gateway**: http://localhost:5000
- **Policy Service**: http://localhost:5001
- **Claim Service**: http://localhost:5002

## 🔐 Default Admin Credentials

- **Username**: admin@ims.com
- **Password**: admin123

## 📊 Health Checks

The system includes health checks for all services:

```bash
# Check service status
docker-compose ps

# Check individual service health
curl http://localhost:5000/api/health
curl http://localhost:5001/health
curl http://localhost:5002/health
```

## 🔧 Configuration

### Environment Variables

You can override default settings using environment variables:

```bash
# Custom ports
GATEWAY_PORT=5000 docker-compose up

# Database settings
DB_PATH=/custom/path docker-compose up
```

### Custom Configuration

1. Create a `.env` file in the root directory:

```env
# Custom ports
FRONTEND_PORT=4200
GATEWAY_PORT=5000
POLICY_PORT=5001
CLAIM_PORT=5002

# Environment
FLASK_ENV=development
NODE_ENV=development
```

2. The docker-compose will automatically load these variables.

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**

   ```bash
   # Check what's using the port
   lsof -i :5000

   # Kill the process
   kill -9 <PID>
   ```

2. **Services Not Starting**

   ```bash
   # Check logs
   docker-compose logs gateway

   # Rebuild clean
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Database Issues**

   ```bash
   # Reset databases
   docker-compose down -v
   docker-compose up --build
   ```

4. **Frontend Build Errors**
   ```bash
   # Clear node modules and rebuild
   docker-compose exec frontend rm -rf node_modules
   docker-compose restart frontend
   ```

### Performance Optimization

1. **Increase Memory Limits**

   ```yaml
   # In docker-compose.yml
   services:
     frontend:
       deploy:
         resources:
           limits:
             memory: 1GB
   ```

2. **Use Multi-stage Builds**
   - Already implemented in Dockerfiles for optimal image sizes

## 📁 Project Structure

```
main/
├── backend/
│   ├── gateway/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── policyservice/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── claimservice/
│      ├── Dockerfile
│      ├── app.py
│      └── requirements.txt
│   
├── frontend/
│   └── ims-frontend/
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── package.json
│       └── src/
├── docker-compose.yml           # Production setup
├── docker-compose.dev.yml       # Development setup
└── README-DOCKER.md            # This file
```

## 🔒 Security Considerations

- All services communicate through an internal Docker network
- Frontend uses Nginx reverse proxy for API calls
- JWT tokens are used for authentication
- File uploads are handled securely
- Database files are persisted in Docker volumes

## 🚀 Deployment

For production deployment:

1. Use the production docker-compose.yml
2. Set environment variables for production
3. Configure proper logging and monitoring
4. Set up SSL certificates if needed
5. Consider using Docker Swarm or Kubernetes for scaling

## 📝 Development Tips

- Use `docker-compose.dev.yml` for development with hot reloading
- Mount source code volumes for immediate changes
- Check logs regularly: `docker-compose logs -f`
- Use health checks to ensure services are ready

## 🤝 Contributing

1. Make changes to source code
2. Test with development docker-compose
3. Ensure all services pass health checks
4. Update documentation if needed

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify all services are healthy: `docker-compose ps`
3. Ensure ports are not conflicting: `lsof -i :PORT`
4. Try rebuilding: `docker-compose build --no-cache`
