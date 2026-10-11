import pytest
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

@pytest.fixture
def sample_apple_10k_text():
    sample_file = backend_dir / "app" / "data" / "sample_documents" / "apple_10k_fy24.txt"
    return sample_file.read_text(encoding="utf-8")

@pytest.fixture
def sample_nvidia_10q_text():
    sample_file = backend_dir / "app" / "data" / "sample_documents" / "nvidia_q2_fy25.txt"
    return sample_file.read_text(encoding="utf-8")

@pytest.fixture
def sample_barclays_memo_text():
    sample_file = backend_dir / "app" / "data" / "sample_documents" / "barclays_credit_memo.txt"
    return sample_file.read_text(encoding="utf-8")
