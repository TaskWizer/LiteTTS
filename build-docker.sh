#!/bin/bash
set -euo pipefail

# LiteTTS Docker Build Script
# Supports multi-architecture builds and optimization

# Configuration
IMAGE_NAME="litetts"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"
ENVIRONMENT="${ENVIRONMENT:-production}"
BUILD_PLATFORMS="${BUILD_PLATFORMS:-linux/amd64,linux/arm64}"
PUSH_IMAGE="${PUSH_IMAGE:-false}"
CACHE_FROM="${CACHE_FROM:-}"
CACHE_TO="${CACHE_TO:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
LiteTTS Docker Build Script

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -t, --tag TAG           Image tag (default: latest)
    -r, --registry REGISTRY Registry prefix (e.g., ghcr.io/username)
    -e, --env ENVIRONMENT   Build environment (default: production)
    -p, --platforms PLATFORMS Build platforms (default: linux/amd64,linux/arm64)
    --push                  Push image to registry
    --cache-from SOURCE     Cache source for build
    --cache-to DEST         Cache destination for build
    --single-arch           Build for current architecture only
    --no-cache              Disable build cache
    --dry-run               Show commands without executing

Examples:
    $0                                          # Build for current architecture
    $0 --tag v1.0.0 --push                    # Build and push with tag
    $0 --platforms linux/amd64 --single-arch  # Build for AMD64 only
    $0 --registry ghcr.io/username --push     # Build and push to registry
    $0 --cache-from type=registry,ref=litetts:cache # Use registry cache

Environment Variables:
    IMAGE_TAG               Image tag (default: latest)
    REGISTRY                Registry prefix
    ENVIRONMENT             Build environment (default: production)
    BUILD_PLATFORMS         Build platforms (default: linux/amd64,linux/arm64)
    PUSH_IMAGE              Push to registry (true/false)
    CACHE_FROM              Cache source
    CACHE_TO                Cache destination
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--platforms)
            BUILD_PLATFORMS="$2"
            shift 2
            ;;
        --push)
            PUSH_IMAGE="true"
            shift
            ;;
        --cache-from)
            CACHE_FROM="$2"
            shift 2
            ;;
        --cache-to)
            CACHE_TO="$2"
            shift 2
            ;;
        --single-arch)
            BUILD_PLATFORMS="$(docker version --format '{{.Server.Os}}/{{.Server.Arch}}')"
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Construct full image name
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
if [[ -n "${REGISTRY}" ]]; then
    FULL_IMAGE_NAME="${REGISTRY}/${FULL_IMAGE_NAME}"
fi

# Pre-build checks
log_info "Starting LiteTTS Docker build..."
log_info "Image: ${FULL_IMAGE_NAME}"
log_info "Environment: ${ENVIRONMENT}"
log_info "Platforms: ${BUILD_PLATFORMS}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if buildx is available for multi-arch builds
if [[ "${BUILD_PLATFORMS}" == *","* ]] && ! docker buildx version &> /dev/null; then
    log_error "Docker buildx is required for multi-architecture builds"
    exit 1
fi

# Check if Dockerfile exists
if [[ ! -f "Dockerfile" ]]; then
    log_error "Dockerfile not found in current directory"
    exit 1
fi

# Create buildx builder if needed for multi-arch
if [[ "${BUILD_PLATFORMS}" == *","* ]]; then
    log_info "Setting up buildx builder for multi-architecture build..."
    if [[ "${DRY_RUN:-}" != "true" ]]; then
        docker buildx create --name litetts-builder --use --bootstrap 2>/dev/null || true
    else
        echo "docker buildx create --name litetts-builder --use --bootstrap"
    fi
fi

# Construct build command
BUILD_CMD="docker"
if [[ "${BUILD_PLATFORMS}" == *","* ]]; then
    BUILD_CMD="${BUILD_CMD} buildx build"
    BUILD_CMD="${BUILD_CMD} --platform ${BUILD_PLATFORMS}"
else
    BUILD_CMD="${BUILD_CMD} build"
fi

BUILD_CMD="${BUILD_CMD} --tag ${FULL_IMAGE_NAME}"
BUILD_CMD="${BUILD_CMD} --build-arg ENVIRONMENT=${ENVIRONMENT}"
BUILD_CMD="${BUILD_CMD} --build-arg BUILDKIT_INLINE_CACHE=1"

# Add cache options
if [[ -n "${CACHE_FROM}" ]]; then
    BUILD_CMD="${BUILD_CMD} --cache-from ${CACHE_FROM}"
fi

if [[ -n "${CACHE_TO}" ]]; then
    BUILD_CMD="${BUILD_CMD} --cache-to ${CACHE_TO}"
fi

# Add no-cache option if specified
if [[ -n "${NO_CACHE:-}" ]]; then
    BUILD_CMD="${BUILD_CMD} ${NO_CACHE}"
fi

# Add push option for multi-arch builds
if [[ "${PUSH_IMAGE}" == "true" ]]; then
    if [[ "${BUILD_PLATFORMS}" == *","* ]]; then
        BUILD_CMD="${BUILD_CMD} --push"
    fi
fi

# Add context
BUILD_CMD="${BUILD_CMD} ."

# Execute build command
log_info "Executing build command:"
log_info "${BUILD_CMD}"

if [[ "${DRY_RUN:-}" == "true" ]]; then
    log_warning "Dry run mode - command not executed"
    exit 0
fi

# Run the build
if eval "${BUILD_CMD}"; then
    log_success "Docker build completed successfully"
else
    log_error "Docker build failed"
    exit 1
fi

# Push single-arch image if needed
if [[ "${PUSH_IMAGE}" == "true" ]] && [[ "${BUILD_PLATFORMS}" != *","* ]]; then
    log_info "Pushing image to registry..."
    if docker push "${FULL_IMAGE_NAME}"; then
        log_success "Image pushed successfully"
    else
        log_error "Failed to push image"
        exit 1
    fi
fi

# Show image size
if [[ "${BUILD_PLATFORMS}" != *","* ]]; then
    log_info "Image size:"
    docker images "${FULL_IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
fi

log_success "Build process completed!"
log_info "Image: ${FULL_IMAGE_NAME}"

# Cleanup buildx builder if created
if [[ "${BUILD_PLATFORMS}" == *","* ]]; then
    log_info "Cleaning up buildx builder..."
    docker buildx rm litetts-builder 2>/dev/null || true
fi
