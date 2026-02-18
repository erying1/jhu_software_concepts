"""Helper utilities for testing"""

from unittest.mock import MagicMock


def create_mock_cursor(fetchone_result=None, rowcount=1):
    """Create a properly mocked database cursor with context manager support"""
    mock_cursor = MagicMock()

    if fetchone_result is not None:
        mock_cursor.fetchone.return_value = fetchone_result

    mock_cursor.rowcount = rowcount

    return mock_cursor


def create_mock_connection(cursor_results=None):
    """Create a mock connection that returns properly configured cursors"""
    mock_conn = MagicMock()

    if cursor_results is None:
        # Single cursor
        mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
    elif isinstance(cursor_results, list):
        # Multiple cursors for multiple queries
        cursors = [
            create_mock_cursor(fetchone_result=result) for result in cursor_results
        ]
        cursor_iter = iter(cursors)

        def get_next_cursor():
            cursor = next(cursor_iter)
            mock_ctx = MagicMock()
            mock_ctx.__enter__.return_value = cursor
            mock_ctx.__exit__.return_value = None
            return mock_ctx

        mock_conn.cursor.side_effect = get_next_cursor
    else:
        # Single cursor with specific result
        mock_cursor = create_mock_cursor(fetchone_result=cursor_results)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None

    return mock_conn
