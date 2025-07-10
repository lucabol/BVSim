"""Common Pydantic schemas used across the application."""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: bool = Field(default=True, description="Indicates this is an error response")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class SuccessResponse(BaseModel):
    """Standard success response schema."""
    
    success: bool = Field(default=True, description="Indicates this is a success response")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class HealthCheck(BaseModel):
    """Health check response schema."""
    
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Application version")
    
    # Database connectivity
    database_connected: bool = Field(..., description="Database connection status")
    database_response_time_ms: Optional[float] = Field(None, description="Database response time")
    
    # Redis connectivity (if enabled)
    redis_connected: Optional[bool] = Field(None, description="Redis connection status")
    redis_response_time_ms: Optional[float] = Field(None, description="Redis response time")
    
    # System metrics
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")
    
    # Service-specific health
    simulation_engine_status: Optional[str] = Field(None, description="Simulation engine status")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database_connected": True,
                "database_response_time_ms": 15.2,
                "uptime_seconds": 3600.0,
                "simulation_engine_status": "ready"
            }
        }


class BulkOperationResult(BaseModel):
    """Result of bulk operations (imports, exports, batch processing)."""
    
    operation_id: str = Field(..., description="Unique operation identifier")
    operation_type: str = Field(..., description="Type of operation performed")
    status: str = Field(..., description="Operation status")
    
    # Counts
    total_items: int = Field(..., description="Total items processed")
    successful_items: int = Field(..., description="Successfully processed items")
    failed_items: int = Field(..., description="Failed items")
    skipped_items: int = Field(default=0, description="Skipped items")
    
    # Timing
    started_at: datetime = Field(..., description="Operation start time")
    completed_at: Optional[datetime] = Field(None, description="Operation completion time")
    duration_seconds: Optional[float] = Field(None, description="Operation duration")
    
    # Results
    success_rate: float = Field(..., description="Success rate percentage")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    warnings: List[str] = Field(default_factory=list, description="List of warning messages")
    
    # Additional data
    result_summary: Optional[Dict[str, Any]] = Field(None, description="Operation summary data")
    download_url: Optional[str] = Field(None, description="Download URL for results")


class ValidationError(BaseModel):
    """Validation error details."""
    
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Value that failed validation")
    constraint: Optional[str] = Field(None, description="Validation constraint that was violated")


class FileUploadResponse(BaseModel):
    """Response for file upload operations."""
    
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File content type")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Processing status
    processing_status: str = Field(default="pending", description="File processing status")
    processing_errors: List[str] = Field(default_factory=list, description="Processing errors")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional file metadata")


class ExportRequest(BaseModel):
    """Base schema for export requests."""
    
    format: str = Field(..., description="Export format (json, csv, excel)")
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    date_format: str = Field(default="ISO", description="Date format for export")
    timezone: str = Field(default="UTC", description="Timezone for timestamps")
    
    # Filtering options
    filters: Optional[Dict[str, Any]] = Field(None, description="Export filters")
    fields: Optional[List[str]] = Field(None, description="Specific fields to export")


class ImportRequest(BaseModel):
    """Base schema for import requests."""
    
    file_id: str = Field(..., description="Uploaded file identifier")
    format: str = Field(..., description="File format (csv, excel, json)")
    
    # Import options
    skip_validation: bool = Field(default=False, description="Skip validation during import")
    update_existing: bool = Field(default=False, description="Update existing records")
    delete_missing: bool = Field(default=False, description="Delete records not in import")
    
    # Mapping options
    field_mapping: Optional[Dict[str, str]] = Field(None, description="Field name mapping")
    default_values: Optional[Dict[str, Any]] = Field(None, description="Default values for missing fields")


class BatchRequest(BaseModel):
    """Base schema for batch operation requests."""
    
    operation_type: str = Field(..., description="Type of batch operation")
    items: List[Dict[str, Any]] = Field(..., description="Items to process")
    
    # Batch options
    fail_on_error: bool = Field(default=False, description="Stop processing on first error")
    batch_size: int = Field(default=100, description="Number of items to process per batch")
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    
    # Validation options
    validate_before_processing: bool = Field(default=True, description="Validate all items before processing")
    skip_duplicates: bool = Field(default=False, description="Skip duplicate items")


class APIInfo(BaseModel):
    """API information schema."""
    
    title: str = Field(..., description="API title")
    version: str = Field(..., description="API version")
    description: str = Field(..., description="API description")
    contact: Optional[Dict[str, str]] = Field(None, description="Contact information")
    license: Optional[Dict[str, str]] = Field(None, description="License information")
    
    # Endpoints summary
    total_endpoints: int = Field(..., description="Total number of endpoints")
    health_check_url: str = Field(..., description="Health check endpoint URL")
    documentation_url: str = Field(..., description="API documentation URL")
    
    # Capabilities
    features: List[str] = Field(..., description="List of supported features")
    supported_formats: List[str] = Field(..., description="Supported data formats")
