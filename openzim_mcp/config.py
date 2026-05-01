"""Configuration management for OpenZIM MCP server."""

import logging
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .defaults import CACHE, CONTENT
from .exceptions import OpenZimMcpConfigurationError


class CacheConfig(BaseModel):
    """Cache configuration settings."""

    enabled: bool = True
    max_size: int = Field(default=CACHE.MAX_SIZE, ge=1, le=10000)
    ttl_seconds: int = Field(default=CACHE.TTL_SECONDS, ge=60, le=86400)
    persistence_enabled: bool = Field(default=CACHE.PERSISTENCE_ENABLED)
    persistence_path: str = Field(default=CACHE.PERSISTENCE_PATH)


class ContentConfig(BaseModel):
    """Content processing configuration."""

    max_content_length: int = Field(default=CONTENT.MAX_CONTENT_LENGTH, ge=100)
    snippet_length: int = Field(default=CONTENT.SNIPPET_LENGTH, ge=100)
    default_search_limit: int = Field(default=CONTENT.SEARCH_LIMIT, ge=1, le=100)


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class OpenZimMcpConfig(BaseSettings):
    """Main configuration for OpenZIM MCP server."""

    # Directory settings
    allowed_directories: List[str] = Field(default_factory=list)

    # Component configurations
    cache: CacheConfig = Field(default_factory=CacheConfig)
    content: ContentConfig = Field(default_factory=ContentConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    # Server settings
    server_name: str = "openzim-mcp"

    model_config = SettingsConfigDict(
        env_prefix="OPENZIM_MCP_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    @field_validator("allowed_directories")
    @classmethod
    def validate_directories(cls, v: List[str]) -> List[str]:
        """Validate that all directories exist and are accessible."""
        if not v:
            raise OpenZimMcpConfigurationError(
                "At least one allowed directory must be specified"
            )

        validated_dirs = []
        for dir_path in v:
            path = Path(dir_path).expanduser().resolve()
            if not path.exists():
                raise OpenZimMcpConfigurationError(f"Directory does not exist: {path}")
            if not path.is_dir():
                raise OpenZimMcpConfigurationError(f"Path is not a directory: {path}")
            validated_dirs.append(str(path))

        return validated_dirs

    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.logging.level),
            format=self.logging.format,
            force=True,
        )
