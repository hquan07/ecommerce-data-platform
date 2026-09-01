import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Fix the import path so 'from rules import RULES' works inside validators.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/quality')))

from src.quality.validators import run_quality_checks
from src.quality.rules import RULES

@patch('src.quality.validators.psycopg2.connect')
def test_run_quality_checks_success(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    # Return 0 nulls for the query
    mock_cur.fetchone.return_value = (0,)
    
    run_quality_checks()
    
    assert mock_cur.execute.call_count >= 1

@patch('src.quality.validators.psycopg2.connect')
def test_run_quality_checks_failure(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur
    
    # Return 10 nulls to trigger a failure
    mock_cur.fetchone.return_value = (10,)
    
    with pytest.raises(ValueError, match="Data Quality Violation"):
        run_quality_checks()
