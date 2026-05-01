"""
Async wrappers for ZIM operations.

This module provides async versions of ZimOperations methods by wrapping
the synchronous operations with asyncio.to_thread() to prevent blocking
the event loop during I/O-bound operations.
"""

import asyncio
import logging
from typing import Optional

from .zim_operations import ZimOperations

logger = logging.getLogger(__name__)


class AsyncZimOperations:
    """Async wrapper for ZimOperations.

    Provides async versions of all ZimOperations methods that run
    the underlying sync operations in a thread pool to prevent
    blocking the event loop.
    """

    def __init__(self, zim_operations: ZimOperations):
        """Initialize async operations wrapper.

        Args:
            zim_operations: Underlying synchronous ZimOperations instance
        """
        self._ops = zim_operations
        logger.debug("AsyncZimOperations initialized")

    @property
    def sync_ops(self) -> ZimOperations:
        """Access the underlying synchronous operations."""
        return self._ops

    async def list_zim_files_data(self) -> list:
        """List all ZIM files as structured data (async)."""
        return await asyncio.to_thread(self._ops.list_zim_files_data)

    async def search_zim_file(
        self,
        zim_file_path: str,
        query: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> str:
        """Search within ZIM file content (async)."""
        return await asyncio.to_thread(
            self._ops.search_zim_file, zim_file_path, query, limit, offset
        )

    async def get_zim_entry(
        self,
        zim_file_path: str,
        entry_path: str,
        max_content_length: Optional[int] = None,
        content_offset: int = 0,
    ) -> str:
        """Get an entry from a ZIM file (async)."""
        return await asyncio.to_thread(
            self._ops.get_zim_entry,
            zim_file_path,
            entry_path,
            max_content_length,
            content_offset,
        )

    async def list_namespaces(self, zim_file_path: str) -> str:
        """List all namespaces in a ZIM file (async)."""
        return await asyncio.to_thread(self._ops.list_namespaces, zim_file_path)

    async def search_with_filters(
        self,
        zim_file_path: str,
        query: str,
        namespace: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> str:
        """Search with filters (async)."""
        return await asyncio.to_thread(
            self._ops.search_with_filters,
            zim_file_path,
            query,
            namespace,
            content_type,
            limit,
            offset,
        )

    async def extract_article_links(
        self,
        zim_file_path: str,
        entry_path: str,
    ) -> str:
        """Extract links from an article (async)."""
        return await asyncio.to_thread(
            self._ops.extract_article_links, zim_file_path, entry_path
        )

    async def get_entry_summary(
        self,
        zim_file_path: str,
        entry_path: str,
        max_words: int = 200,
    ) -> str:
        """Get entry summary (async)."""
        return await asyncio.to_thread(
            self._ops.get_entry_summary, zim_file_path, entry_path, max_words
        )

    async def get_table_of_contents(
        self,
        zim_file_path: str,
        entry_path: str,
    ) -> str:
        """Get table of contents (async)."""
        return await asyncio.to_thread(
            self._ops.get_table_of_contents, zim_file_path, entry_path
        )

    async def search_all(self, query: str, limit_per_file: int = 5) -> str:
        """Search across every ZIM file in allowed dirs (async)."""
        return await asyncio.to_thread(self._ops.search_all, query, limit_per_file)

    async def find_entry_by_title(
        self,
        zim_file_path: str,
        title: str,
        cross_file: bool = False,
        limit: int = 10,
    ) -> str:
        """Resolve title to entry path(s) (async)."""
        return await asyncio.to_thread(
            self._ops.find_entry_by_title,
            zim_file_path,
            title,
            cross_file,
            limit,
        )