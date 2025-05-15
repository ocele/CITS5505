from app.utils import generate_ranking

def test_generate_ranking_empty():
    """Test that generate_ranking returns an empty list when no users are provided."""
    result = generate_ranking([], period="daily")
    assert result == []
