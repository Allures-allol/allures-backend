#!/usr/bin/env bash

# Compose files
DB_COMPOSE_FILE="docker-compose-db.yml"
PRODUCT_COMPOSE_FILE="docker-compose-product-service.yml"
SALES_COMPOSE_FILE="docker-compose-sales-service.yml"
REVIEW_COMPOSE_FILE="docker-compose-review-service.yml"
PROFILE_COMPOSE_FILE="docker-compose-profile_service.yml"
DASHBOARD_COMPOSE_FILE="docker-compose-dashboard_service.yml"
DISCOUNT_COMPOSE_FILE="docker-compose-discount_service.yml"
PAYMENT_COMPOSE_FILE="docker-compose-payment_service.yml"
ADMIN_SERVICE_URL="docker-compose-admin_service.yml"
SUBSCRIPTION_SERVICE_URL="docker-compose-subscription_service.yml"

ALL_FILES="-f $DB_COMPOSE_FILE -f $PRODUCT_COMPOSE_FILE -f $SALES_COMPOSE_FILE -f $REVIEW_COMPOSE_FILE \
-f $PROFILE_COMPOSE_FILE -f $DASHBOARD_COMPOSE_FILE -f $DISCOUNT_COMPOSE_FILE -f $PAYMENT_COMPOSE_FILE -f $ADMIN_SERVICE_URL $SUBSCRIPTION_SERVICE_URL"


# Load .env.review.db files from each service
load_envs() {
  for file in services/product_service/.env.db services/sales_service/.env.db services/review_service/.env.db; do
    [ -f "$file" ] && export $(grep -v '^#' "$file" | xargs)
  done
}

start_all() {
  load_envs
  docker compose $ALL_FILES up -d --build
}

stop_all() {
  docker compose $ALL_FILES down
}

logs_all() {
  docker compose $ALL_FILES logs -f --tail=50
}

status_all() {
  docker compose $ALL_FILES ps
}

clean_docker() {
  echo " Cleaning up unused Docker images and volumes..."
  docker system prune -f
  docker volume prune -f
}

run_single() {
  SERVICE=$1
  case "$SERVICE" in
    product-service)
      docker compose -f $PRODUCT_COMPOSE_FILE up -d --build
      ;;
    sales-service)
      docker compose -f $SALES_COMPOSE_FILE up -d --build
      ;;
    review-service)
      docker compose -f $REVIEW_COMPOSE_FILE up -d --build
      ;;
    profile-service)
      docker compose -f $PROFILE_COMPOSE_FILE up -d --build
      ;;
    dashboard-service)
      docker compose -f $DASHBOARD_COMPOSE_FILE up -d --build
      ;;
    discount-service)
      docker compose -f $DISCOUNT_COMPOSE_FILE up -d --build
      ;;
    payment-service)
      docker compose -f $PAYMENT_COMPOSE_FILE up -d --build
      ;;
    admin-service)
      docker compose -f $ADMIN_SERVICE_URL up -d --build
      ;;
    subscription-service)
      docker compose -f $SUBSCRIPTION_SERVICE_URL up -d --build
      ;;
    db)
      docker compose -f $DB_COMPOSE_FILE up -d --build
      ;;
    *)
      echo " Unknown service: $SERVICE"
      echo " Available services: product-service, sales-service, review-service, profile-service, dashboard-service, discount-service, payment-service, admin-service, subscription-service, db"
      exit 1
      ;;
  esac
}

# Main logic
case "$1" in
  start)
    stop_all
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    stop_all
    start_all
    ;;
  logs)
    logs_all
    ;;
  status)
    status_all
    ;;
  clean)
    clean_docker
    ;;
  run)
    run_single "$2"
    ;;
  *)
    echo "  Usage: $0 {start|stop|restart|logs|status|clean|run <service>}"
    exit 1
    ;;
esac

exit 0
