import pytest
from app.search.hybrid_search import HybridProductSearch

def test_extract_structured_requirements():
    query = "I need a gaming laptop under ₹80,000, 32GB RAM, 1TB SSD, and delivery within 3 days."
    reqs = HybridProductSearch.extract_structured_requirements(query)
    
    assert reqs.budget_max == 80000.0
    assert reqs.min_ram_gb == 32
    assert reqs.min_storage_gb == 1000
    assert reqs.max_delivery_days == 3
    assert reqs.category == "laptops"

def test_extract_k_format_budget():
    query = "laptop for video editing under 85k with 16gb"
    reqs = HybridProductSearch.extract_structured_requirements(query)
    
    assert reqs.budget_max == 85000.0
    assert reqs.min_ram_gb == 16
