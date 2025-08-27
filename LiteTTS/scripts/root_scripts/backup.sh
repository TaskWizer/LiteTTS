#!/bin/bash

# Kokoro ONNX TTS API - Backup Script
# Automated backup system for persistent data with retention policy

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-${PROJECT_ROOT}/backups}"
LOG_FILE="${PROJECT_ROOT}/docs/logs/backup.log"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
COMPRESSION_LEVEL="${COMPRESSION_LEVEL:-6}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${BLUE}$*${NC}"; }
warn() { log "WARN" "${YELLOW}$*${NC}"; }
error() { log "ERROR" "${RED}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }

# Help function
show_help() {
    cat << EOF
Kokoro ONNX TTS API Backup Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    backup          Create a full backup
    restore         Restore from backup
    list            List available backups
    cleanup         Clean up old backups
    verify          Verify backup integrity

Options:
    -d, --dir DIR           Backup directory [default: ./backups]
    -r, --retention DAYS    Retention period in days [default: 7]
    -c, --compression LEVEL Compression level 1-9 [default: 6]
    -f, --force             Force operation without confirmation
    -v, --verbose           Verbose output
    -h, --help              Show this help message

Examples:
    $0 backup                           # Create full backup
    $0 backup -d /external/backups      # Backup to external directory
    $0 restore backup_20240101_120000   # Restore specific backup
    $0 list                             # List all backups
    $0 cleanup                          # Clean old backups

EOF
}

# Parse command line arguments
FORCE=false
VERBOSE=false
COMMAND=""
BACKUP_NAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir)
            BACKUP_BASE_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -c|--compression)
            COMPRESSION_LEVEL="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        backup|restore|list|cleanup|verify)
            COMMAND="$1"
            shift
            ;;
        *)
            if [[ "$COMMAND" == "restore" && -z "$BACKUP_NAME" ]]; then
                BACKUP_NAME="$1"
                shift
            else
                error "Unknown option: $1"
                show_help
                exit 1
            fi
            ;;
    esac
done

# Validate command
if [[ -z "$COMMAND" ]]; then
    error "No command specified"
    show_help
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_BASE_DIR" "$(dirname "$LOG_FILE")"

# Get backup timestamp
get_timestamp() {
    date '+%Y%m%d_%H%M%S'
}

# Get backup size in human readable format
get_size() {
    local path="$1"
    if [[ -f "$path" ]]; then
        du -h "$path" | cut -f1
    elif [[ -d "$path" ]]; then
        du -sh "$path" | cut -f1
    else
        echo "0B"
    fi
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
        exit 1
    fi
}

# Create backup
create_backup() {
    info "Starting backup process..."
    
    check_docker
    
    local timestamp=$(get_timestamp)
    local backup_dir="${BACKUP_BASE_DIR}/backup_${timestamp}"
    
    mkdir -p "$backup_dir"
    
    info "Backup directory: $backup_dir"
    
    # Backup configuration files
    info "Backing up configuration files..."
    cp "$PROJECT_ROOT/config.json" "$backup_dir/" 2>/dev/null || warn "config.json not found"
    
    if [[ -d "$PROJECT_ROOT/config" ]]; then
        cp -r "$PROJECT_ROOT/config" "$backup_dir/"
        success "Configuration files backed up"
    fi
    
    # Backup Docker volumes
    info "Backing up Docker volumes..."
    
    # Models volume (if exists)
    if docker volume ls | grep -q kokoro-models; then
        info "Backing up models volume..."
        docker run --rm \
            -v kokoro-models:/data:ro \
            -v "$backup_dir":/backup \
            alpine:latest \
            tar czf /backup/kokoro-models.tar.gz -C /data .
        success "Models volume backed up"
    fi
    
    # Voices volume (if exists)
    if docker volume ls | grep -q kokoro-voices; then
        info "Backing up voices volume..."
        docker run --rm \
            -v kokoro-voices:/data:ro \
            -v "$backup_dir":/backup \
            alpine:latest \
            tar czf /backup/kokoro-voices.tar.gz -C /data .
        success "Voices volume backed up"
    fi
    
    # Cache volume (if exists)
    if docker volume ls | grep -q kokoro-cache; then
        info "Backing up cache volume..."
        docker run --rm \
            -v kokoro-cache:/data:ro \
            -v "$backup_dir":/backup \
            alpine:latest \
            tar czf /backup/kokoro-cache.tar.gz -C /data .
        success "Cache volume backed up"
    fi
    
    # Logs volume (if exists)
    if docker volume ls | grep -q kokoro-logs; then
        info "Backing up logs volume..."
        docker run --rm \
            -v kokoro-logs:/data:ro \
            -v "$backup_dir":/backup \
            alpine:latest \
            tar czf /backup/kokoro-logs.tar.gz -C /data .
        success "Logs volume backed up"
    fi
    
    # Create backup metadata
    cat > "$backup_dir/backup_info.json" << EOF
{
    "timestamp": "$timestamp",
    "date": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "user": "$(whoami)",
    "docker_version": "$(docker --version)",
    "backup_size": "$(get_size "$backup_dir")",
    "retention_days": $RETENTION_DAYS,
    "compression_level": $COMPRESSION_LEVEL
}
EOF
    
    # Create backup archive
    info "Creating backup archive..."
    cd "$BACKUP_BASE_DIR"
    tar czf "backup_${timestamp}.tar.gz" "backup_${timestamp}/"
    
    # Remove uncompressed backup directory
    rm -rf "backup_${timestamp}/"
    
    local backup_size=$(get_size "backup_${timestamp}.tar.gz")
    success "Backup completed: backup_${timestamp}.tar.gz ($backup_size)"
    
    # Update latest backup symlink
    ln -sf "backup_${timestamp}.tar.gz" "$BACKUP_BASE_DIR/latest_backup.tar.gz"
    
    info "Backup process completed successfully"
}

# List backups
list_backups() {
    info "Available backups in $BACKUP_BASE_DIR:"
    echo "=================================================="
    
    if [[ ! -d "$BACKUP_BASE_DIR" ]]; then
        warn "Backup directory does not exist: $BACKUP_BASE_DIR"
        return 0
    fi
    
    local backup_count=0
    for backup in "$BACKUP_BASE_DIR"/backup_*.tar.gz; do
        if [[ -f "$backup" ]]; then
            local filename=$(basename "$backup")
            local size=$(get_size "$backup")
            local date=$(stat -c %y "$backup" | cut -d' ' -f1)
            
            echo "  $filename"
            echo "    Size: $size"
            echo "    Date: $date"
            echo ""
            
            backup_count=$((backup_count + 1))
        fi
    done
    
    if [[ $backup_count -eq 0 ]]; then
        warn "No backups found"
    else
        info "Total backups: $backup_count"
    fi
}

# Restore backup
restore_backup() {
    if [[ -z "$BACKUP_NAME" ]]; then
        error "Backup name required for restore"
        list_backups
        exit 1
    fi
    
    local backup_file="$BACKUP_BASE_DIR/${BACKUP_NAME}"
    if [[ ! "$backup_file" == *.tar.gz ]]; then
        backup_file="${backup_file}.tar.gz"
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
        list_backups
        exit 1
    fi
    
    if [[ "$FORCE" != true ]]; then
        warn "This will restore from backup and may overwrite current data."
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Restore cancelled"
            exit 0
        fi
    fi
    
    info "Restoring from backup: $(basename "$backup_file")"
    
    check_docker
    
    # Extract backup
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    tar xzf "$backup_file"
    
    local backup_dir=$(find . -name "backup_*" -type d | head -n1)
    if [[ -z "$backup_dir" ]]; then
        error "Invalid backup file structure"
        rm -rf "$temp_dir"
        exit 1
    fi
    
    # Stop services
    info "Stopping services..."
    cd "$PROJECT_ROOT"
    docker-compose down || true
    
    # Restore configuration files
    if [[ -f "$temp_dir/$backup_dir/config.json" ]]; then
        cp "$temp_dir/$backup_dir/config.json" "$PROJECT_ROOT/"
        success "Configuration restored"
    fi
    
    if [[ -d "$temp_dir/$backup_dir/config" ]]; then
        cp -r "$temp_dir/$backup_dir/config" "$PROJECT_ROOT/"
        success "Config directory restored"
    fi
    
    # Restore Docker volumes
    for volume_backup in "$temp_dir/$backup_dir"/*.tar.gz; do
        if [[ -f "$volume_backup" ]]; then
            local volume_name=$(basename "$volume_backup" .tar.gz)
            info "Restoring volume: $volume_name"
            
            # Create volume if it doesn't exist
            docker volume create "$volume_name" >/dev/null 2>&1 || true
            
            # Restore volume data
            docker run --rm \
                -v "$volume_name":/data \
                -v "$temp_dir/$backup_dir":/backup \
                alpine:latest \
                sh -c "rm -rf /data/* && tar xzf /backup/$(basename "$volume_backup") -C /data"
            
            success "Volume $volume_name restored"
        fi
    done
    
    # Cleanup
    rm -rf "$temp_dir"
    
    # Start services
    info "Starting services..."
    docker-compose up -d
    
    success "Restore completed successfully"
}

# Cleanup old backups
cleanup_backups() {
    info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    if [[ ! -d "$BACKUP_BASE_DIR" ]]; then
        warn "Backup directory does not exist: $BACKUP_BASE_DIR"
        return 0
    fi
    
    local deleted_count=0
    
    # Find and delete old backups
    while IFS= read -r -d '' backup; do
        local age_days=$(( ($(date +%s) - $(stat -c %Y "$backup")) / 86400 ))
        
        if [[ $age_days -gt $RETENTION_DAYS ]]; then
            local size=$(get_size "$backup")
            info "Deleting old backup: $(basename "$backup") (${age_days} days old, $size)"
            rm -f "$backup"
            deleted_count=$((deleted_count + 1))
        fi
    done < <(find "$BACKUP_BASE_DIR" -name "backup_*.tar.gz" -print0)
    
    if [[ $deleted_count -eq 0 ]]; then
        info "No old backups to clean up"
    else
        success "Deleted $deleted_count old backup(s)"
    fi
}

# Verify backup integrity
verify_backup() {
    if [[ -z "$BACKUP_NAME" ]]; then
        info "Verifying all backups..."
        for backup in "$BACKUP_BASE_DIR"/backup_*.tar.gz; do
            if [[ -f "$backup" ]]; then
                verify_single_backup "$backup"
            fi
        done
    else
        local backup_file="$BACKUP_BASE_DIR/${BACKUP_NAME}"
        if [[ ! "$backup_file" == *.tar.gz ]]; then
            backup_file="${backup_file}.tar.gz"
        fi
        verify_single_backup "$backup_file"
    fi
}

verify_single_backup() {
    local backup_file="$1"
    local filename=$(basename "$backup_file")
    
    info "Verifying backup: $filename"
    
    if [[ ! -f "$backup_file" ]]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Test archive integrity
    if tar tzf "$backup_file" >/dev/null 2>&1; then
        success "✓ Archive integrity: OK"
    else
        error "✗ Archive integrity: FAILED"
        return 1
    fi
    
    # Check if backup contains expected files
    local has_config=false
    local has_volumes=false
    
    if tar tzf "$backup_file" | grep -q "config.json\|config/"; then
        has_config=true
        success "✓ Configuration files: PRESENT"
    else
        warn "✗ Configuration files: MISSING"
    fi
    
    if tar tzf "$backup_file" | grep -q "\.tar\.gz$"; then
        has_volumes=true
        success "✓ Volume backups: PRESENT"
    else
        warn "✗ Volume backups: MISSING"
    fi
    
    if [[ "$has_config" == true || "$has_volumes" == true ]]; then
        success "Backup verification: PASSED"
        return 0
    else
        error "Backup verification: FAILED"
        return 1
    fi
}

# Main execution
main() {
    case "$COMMAND" in
        backup)
            create_backup
            cleanup_backups
            ;;
        restore)
            restore_backup
            ;;
        list)
            list_backups
            ;;
        cleanup)
            cleanup_backups
            ;;
        verify)
            verify_backup
            ;;
        *)
            error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
