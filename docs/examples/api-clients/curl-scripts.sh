#!/bin/bash

# ScraperV4 cURL API Examples
# 
# This script demonstrates how to interact with ScraperV4's REST API using cURL.
# It provides examples for all major API endpoints with proper error handling,
# JSON formatting, and real-world usage scenarios.
#
# Prerequisites:
# - ScraperV4 server running (default: http://localhost:8080)
# - curl installed
# - jq installed (for JSON formatting - optional but recommended)
#
# Usage:
#   chmod +x curl-scripts.sh
#   ./curl-scripts.sh
#
# Individual function usage:
#   source curl-scripts.sh
#   health_check
#   list_templates
#   create_simple_job "https://example.com" "template-id"

set -e  # Exit on error

# Configuration
SCRAPERV4_URL="${SCRAPERV4_URL:-http://localhost:8080}"
TEMP_DIR="${TEMP_DIR:-/tmp/scraperv4}"
LOG_FILE="${LOG_FILE:-$TEMP_DIR/api.log}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create temp directory
mkdir -p "$TEMP_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Success message function
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Warning message function
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Info message function
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if jq is available for JSON formatting
check_jq() {
    if command -v jq &> /dev/null; then
        return 0
    else
        warning "jq not found. JSON output will not be formatted."
        return 1
    fi
}

# Format JSON output if jq is available
format_json() {
    if check_jq; then
        jq '.'
    else
        cat
    fi
}

# Make API request with error handling
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local extra_args="$4"
    
    local url="$SCRAPERV4_URL$endpoint"
    local curl_args=(-X "$method" -H "Content-Type: application/json" -H "Accept: application/json")
    
    if [ -n "$data" ]; then
        curl_args+=(-d "$data")
    fi
    
    if [ -n "$extra_args" ]; then
        curl_args+=($extra_args)
    fi
    
    log "API Request: $method $url"
    
    local response
    local http_code
    
    response=$(curl -s -w "%{http_code}" "${curl_args[@]}" "$url")
    http_code="${response: -3}"
    response="${response%???}"
    
    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo "$response" | format_json
        return 0
    else
        echo -e "${RED}HTTP $http_code Error:${NC}" >&2
        echo "$response" | format_json >&2
        return 1
    fi
}

# Health Check
health_check() {
    info "Checking API health..."
    
    if api_request "GET" "/api/health"; then
        success "API is healthy"
        return 0
    else
        handle_error "API health check failed"
    fi
}

# List all templates
list_templates() {
    info "Listing templates..."
    
    local include_inactive="${1:-false}"
    local endpoint="/api/templates"
    
    if [ "$include_inactive" = "true" ]; then
        endpoint="$endpoint?include_inactive=true"
    fi
    
    if response=$(api_request "GET" "$endpoint"); then
        local count
        if check_jq; then
            count=$(echo "$response" | jq '.templates | length')
            success "Found $count templates"
        else
            success "Templates listed successfully"
        fi
        echo "$response"
        return 0
    else
        handle_error "Failed to list templates"
    fi
}

# Get specific template
get_template() {
    local template_id="$1"
    
    if [ -z "$template_id" ]; then
        handle_error "Template ID is required"
    fi
    
    info "Getting template: $template_id"
    
    if response=$(api_request "GET" "/api/templates/$template_id"); then
        success "Template retrieved successfully"
        echo "$response"
        return 0
    else
        handle_error "Failed to get template"
    fi
}

# Create a new template
create_template() {
    local template_file="$1"
    
    if [ -z "$template_file" ]; then
        handle_error "Template file path is required"
    fi
    
    if [ ! -f "$template_file" ]; then
        handle_error "Template file not found: $template_file"
    fi
    
    info "Creating template from file: $template_file"
    
    local template_data
    template_data=$(cat "$template_file")
    
    if response=$(api_request "POST" "/api/templates" "$template_data"); then
        local template_id
        if check_jq; then
            template_id=$(echo "$response" | jq -r '.id // .template_id // "unknown"')
            success "Template created with ID: $template_id"
        else
            success "Template created successfully"
        fi
        echo "$response"
        return 0
    else
        handle_error "Failed to create template"
    fi
}

# Test template against URL
test_template() {
    local template_id="$1"
    local test_url="$2"
    
    if [ -z "$template_id" ] || [ -z "$test_url" ]; then
        handle_error "Template ID and test URL are required"
    fi
    
    info "Testing template $template_id against $test_url"
    
    local test_data="{\"url\": \"$test_url\"}"
    
    if response=$(api_request "POST" "/api/templates/$template_id/test" "$test_data"); then
        local success_status
        if check_jq; then
            success_status=$(echo "$response" | jq -r '.success // false')
            if [ "$success_status" = "true" ]; then
                success "Template test successful"
            else
                warning "Template test completed but may have issues"
            fi
        else
            success "Template test completed"
        fi
        echo "$response"
        return 0
    else
        handle_error "Template test failed"
    fi
}

# Create a scraping job
create_job() {
    local name="$1"
    local template_id="$2"
    local target_url="$3"
    local config="$4"
    
    if [ -z "$name" ] || [ -z "$template_id" ] || [ -z "$target_url" ]; then
        handle_error "Job name, template ID, and target URL are required"
    fi
    
    info "Creating job: $name"
    
    local job_data
    if [ -n "$config" ]; then
        job_data="{
            \"name\": \"$name\",
            \"template_id\": \"$template_id\",
            \"target_url\": \"$target_url\",
            \"config\": $config
        }"
    else
        job_data="{
            \"name\": \"$name\",
            \"template_id\": \"$template_id\",
            \"target_url\": \"$target_url\",
            \"config\": {}
        }"
    fi
    
    if response=$(api_request "POST" "/api/scraping/jobs" "$job_data"); then
        local job_id
        if check_jq; then
            job_id=$(echo "$response" | jq -r '.job_id // .id // "unknown"')
            success "Job created with ID: $job_id"
        else
            success "Job created successfully"
        fi
        echo "$response"
        return 0
    else
        handle_error "Failed to create job"
    fi
}

# Start a scraping job
start_job() {
    local job_id="$1"
    
    if [ -z "$job_id" ]; then
        handle_error "Job ID is required"
    fi
    
    info "Starting job: $job_id"
    
    local start_data="{\"job_id\": \"$job_id\"}"
    
    if response=$(api_request "POST" "/api/scraping/start" "$start_data"); then
        success "Job started successfully"
        echo "$response"
        return 0
    else
        handle_error "Failed to start job"
    fi
}

# Get job status
get_job_status() {
    local job_id="$1"
    
    if [ -z "$job_id" ]; then
        handle_error "Job ID is required"
    fi
    
    if response=$(api_request "GET" "/api/scraping/status/$job_id"); then
        local status
        local progress
        if check_jq; then
            status=$(echo "$response" | jq -r '.status // "unknown"')
            progress=$(echo "$response" | jq -r '.progress // 0')
            info "Job $job_id - Status: $status, Progress: $progress%"
        else
            info "Job status retrieved"
        fi
        echo "$response"
        return 0
    else
        handle_error "Failed to get job status"
    fi
}

# Monitor job until completion
monitor_job() {
    local job_id="$1"
    local poll_interval="${2:-3}"
    
    if [ -z "$job_id" ]; then
        handle_error "Job ID is required"
    fi
    
    info "Monitoring job: $job_id (polling every ${poll_interval}s)"
    
    while true; do
        if response=$(get_job_status "$job_id" 2>/dev/null); then
            local status
            if check_jq; then
                status=$(echo "$response" | jq -r '.status // "unknown"')
                case "$status" in
                    "completed")
                        success "Job $job_id completed successfully"
                        echo "$response"
                        return 0
                        ;;
                    "failed"|"error"|"stopped")
                        warning "Job $job_id finished with status: $status"
                        echo "$response"
                        return 1
                        ;;
                    *)
                        # Job still running
                        ;;
                esac
            fi
        else
            warning "Failed to get job status, retrying..."
        fi
        
        sleep "$poll_interval"
    done
}

# Stop a running job
stop_job() {
    local job_id="$1"
    
    if [ -z "$job_id" ]; then
        handle_error "Job ID is required"
    fi
    
    info "Stopping job: $job_id"
    
    if response=$(api_request "POST" "/api/scraping/stop/$job_id"); then
        success "Job stop request sent"
        echo "$response"
        return 0
    else
        handle_error "Failed to stop job"
    fi
}

# List jobs with optional filtering
list_jobs() {
    local status_filter="$1"
    local limit="${2:-50}"
    local offset="${3:-0}"
    
    info "Listing jobs..."
    
    local endpoint="/api/scraping/jobs?limit=$limit&offset=$offset"
    if [ -n "$status_filter" ]; then
        endpoint="$endpoint&status=$status_filter"
    fi
    
    if response=$(api_request "GET" "$endpoint"); then
        local count
        if check_jq; then
            count=$(echo "$response" | jq '.jobs | length')
            success "Found $count jobs"
        else
            success "Jobs listed successfully"
        fi
        echo "$response"
        return 0
    else
        handle_error "Failed to list jobs"
    fi
}

# Get job results
get_job_results() {
    local job_id="$1"
    local limit="${2:-100}"
    local offset="${3:-0}"
    
    if [ -z "$job_id" ]; then
        handle_error "Job ID is required"
    fi
    
    info "Getting results for job: $job_id"
    
    local endpoint="/api/data/results/$job_id"
    if [ "$limit" != "100" ] || [ "$offset" != "0" ]; then
        endpoint="$endpoint?limit=$limit&offset=$offset"
    fi
    
    if response=$(api_request "GET" "$endpoint"); then
        local count
        if check_jq; then
            count=$(echo "$response" | jq '.results | length')
            success "Retrieved $count results"
        else
            success "Results retrieved successfully"
        fi
        echo "$response"
        return 0
    else
        handle_error "Failed to get job results"
    fi
}

# Export job data
export_job_data() {
    local job_id="$1"
    local format="${2:-json}"
    local include_metadata="${3:-true}"
    local output_file="$4"
    
    if [ -z "$job_id" ]; then
        handle_error "Job ID is required"
    fi
    
    info "Exporting job data: $job_id (format: $format)"
    
    local export_data="{
        \"job_id\": \"$job_id\",
        \"format\": \"$format\",
        \"include_metadata\": $include_metadata
    }"
    
    if response=$(api_request "POST" "/api/data/export" "$export_data"); then
        local file_path
        if check_jq; then
            file_path=$(echo "$response" | jq -r '.file_path // ""')
            if [ -n "$file_path" ] && [ -n "$output_file" ]; then
                # Download the exported file
                local download_url
                if [[ "$file_path" =~ ^https?:// ]]; then
                    download_url="$file_path"
                else
                    download_url="$SCRAPERV4_URL$file_path"
                fi
                
                info "Downloading exported file to: $output_file"
                if curl -s -o "$output_file" "$download_url"; then
                    success "File downloaded: $output_file"
                else
                    warning "Failed to download file"
                fi
            fi
        fi
        
        success "Data export completed"
        echo "$response"
        return 0
    else
        handle_error "Failed to export job data"
    fi
}

# Preview scraping without creating a job
preview_scraping() {
    local url="$1"
    local template_id="$2"
    
    if [ -z "$url" ]; then
        handle_error "URL is required"
    fi
    
    info "Previewing scraping for: $url"
    
    local preview_data
    if [ -n "$template_id" ]; then
        preview_data="{\"url\": \"$url\", \"template_id\": \"$template_id\"}"
    else
        preview_data="{\"url\": \"$url\"}"
    fi
    
    if response=$(api_request "POST" "/api/scraping/preview" "$preview_data"); then
        success "Preview completed"
        echo "$response"
        return 0
    else
        handle_error "Preview failed"
    fi
}

# Get system statistics
get_system_stats() {
    info "Getting system statistics..."
    
    if response=$(api_request "GET" "/api/data/stats"); then
        success "System stats retrieved"
        echo "$response"
        return 0
    else
        handle_error "Failed to get system stats"
    fi
}

# Complete workflow: create job, start, monitor, and export
create_simple_job() {
    local url="$1"
    local template_id="$2"
    local job_name="${3:-Quick Scrape $(date '+%Y%m%d_%H%M%S')}"
    local export_format="${4:-json}"
    
    if [ -z "$url" ] || [ -z "$template_id" ]; then
        handle_error "URL and template ID are required"
    fi
    
    info "Starting complete scraping workflow for: $url"
    
    # Create job
    local job_response
    if job_response=$(create_job "$job_name" "$template_id" "$url"); then
        local job_id
        if check_jq; then
            job_id=$(echo "$job_response" | jq -r '.job_id // .id')
        else
            # Extract job ID manually if jq not available
            job_id=$(echo "$job_response" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
        fi
        
        if [ -n "$job_id" ] && [ "$job_id" != "null" ]; then
            # Start job
            start_job "$job_id"
            
            # Monitor job
            if monitor_job "$job_id"; then
                # Get results
                get_job_results "$job_id"
                
                # Export if requested
                if [ "$export_format" != "none" ]; then
                    local export_file="$TEMP_DIR/export_${job_id}.${export_format}"
                    export_job_data "$job_id" "$export_format" "true" "$export_file"
                fi
                
                success "Complete workflow finished successfully"
                return 0
            else
                warning "Job monitoring indicated failure"
                return 1
            fi
        else
            handle_error "Could not extract job ID from response"
        fi
    else
        handle_error "Failed to create job"
    fi
}

# Batch operations
batch_test_templates() {
    local test_url="$1"
    
    if [ -z "$test_url" ]; then
        handle_error "Test URL is required"
    fi
    
    info "Testing all templates against: $test_url"
    
    local templates_response
    if templates_response=$(list_templates); then
        if check_jq; then
            local template_ids
            template_ids=$(echo "$templates_response" | jq -r '.templates[].id')
            
            local success_count=0
            local total_count=0
            
            while IFS= read -r template_id; do
                if [ -n "$template_id" ]; then
                    total_count=$((total_count + 1))
                    info "Testing template: $template_id"
                    
                    if test_template "$template_id" "$test_url" >/dev/null 2>&1; then
                        success_count=$((success_count + 1))
                        success "Template $template_id: PASSED"
                    else
                        warning "Template $template_id: FAILED"
                    fi
                fi
            done <<< "$template_ids"
            
            success "Batch testing completed: $success_count/$total_count templates passed"
        else
            warning "Cannot parse templates without jq"
        fi
    else
        handle_error "Failed to get templates for batch testing"
    fi
}

# Create example template
create_example_template() {
    local template_file="$TEMP_DIR/example_template.json"
    
    info "Creating example template file: $template_file"
    
    cat > "$template_file" << 'EOF'
{
  "name": "example_basic_template",
  "description": "Basic template for general web scraping",
  "version": "1.0.0",
  "fetcher_config": {
    "type": "basic",
    "basic": {
      "timeout": 30,
      "headers": {
        "User-Agent": "Mozilla/5.0 (compatible; ScraperV4/3.0)"
      }
    }
  },
  "selectors": {
    "title": {
      "selector": "title, h1, .title, .main-title",
      "type": "text",
      "auto_save": true
    },
    "content": {
      "selector": ".content, .main-content, .article-content, main",
      "type": "text",
      "auto_save": true
    },
    "links": {
      "selector": "a[href]",
      "type": "all",
      "auto_save": true,
      "attribute": "href"
    }
  },
  "pagination": {
    "enabled": false
  },
  "post_processing": [
    {
      "type": "strip",
      "field": "title"
    },
    {
      "type": "strip",
      "field": "content"
    }
  ],
  "validation_rules": {
    "required_fields": ["title"],
    "field_types": {
      "title": "string",
      "content": "string",
      "links": "list"
    }
  },
  "is_active": true
}
EOF
    
    success "Example template created: $template_file"
    
    # Create the template
    create_template "$template_file"
}

# Help function
show_help() {
    echo "ScraperV4 cURL API Examples"
    echo "Usage: $0 [function_name] [arguments...]"
    echo ""
    echo "Available functions:"
    echo "  health_check                              - Check API health"
    echo "  list_templates [include_inactive]        - List all templates"
    echo "  get_template <template_id>                - Get specific template"
    echo "  create_template <template_file>           - Create template from JSON file"
    echo "  test_template <template_id> <url>         - Test template against URL"
    echo "  create_job <name> <template_id> <url>     - Create scraping job"
    echo "  start_job <job_id>                        - Start job"
    echo "  get_job_status <job_id>                   - Get job status"
    echo "  monitor_job <job_id> [interval]           - Monitor job until completion"
    echo "  stop_job <job_id>                         - Stop running job"
    echo "  list_jobs [status] [limit] [offset]       - List jobs with filtering"
    echo "  get_job_results <job_id>                  - Get job results"
    echo "  export_job_data <job_id> [format] [metadata] [file] - Export job data"
    echo "  preview_scraping <url> [template_id]      - Preview scraping"
    echo "  get_system_stats                          - Get system statistics"
    echo "  create_simple_job <url> <template_id>     - Complete workflow"
    echo "  batch_test_templates <url>                - Test all templates"
    echo "  create_example_template                   - Create example template"
    echo ""
    echo "Environment variables:"
    echo "  SCRAPERV4_URL - ScraperV4 server URL (default: http://localhost:8080)"
    echo "  TEMP_DIR      - Temporary directory (default: /tmp/scraperv4)"
    echo "  LOG_FILE      - Log file path (default: \$TEMP_DIR/api.log)"
    echo ""
    echo "Examples:"
    echo "  $0 health_check"
    echo "  $0 list_templates"
    echo "  $0 create_simple_job https://example.com template-123"
    echo "  $0 batch_test_templates https://httpbin.org/html"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        info "Running ScraperV4 API demonstration..."
        
        # Run demonstration
        health_check
        echo ""
        
        list_templates
        echo ""
        
        get_system_stats
        echo ""
        
        info "Demonstration completed. Use '$0 help' for more options."
    else
        case "$1" in
            "help"|"-h"|"--help")
                show_help
                ;;
            *)
                # Execute the requested function with remaining arguments
                if declare -f "$1" > /dev/null; then
                    "$@"
                else
                    handle_error "Unknown function: $1. Use '$0 help' for available functions."
                fi
                ;;
        esac
    fi
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi