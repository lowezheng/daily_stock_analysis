# -*- coding: utf-8 -*-
"""
AkShare News Provider Integration Tests

Test scope:
1. AkShareNewsProvider - Individual stock news
2. AkShareFlashProvider - Financial flash news
3. SearchService integration - A-share priority strategy
4. Error handling and fallback
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pandas as pd

from src.search_service import (
    SearchService,
    AkShareNewsProvider,
    AkShareFlashProvider,
    SearchResponse,
    SearchResult,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def mock_akshare_news_data():
    """Mock AkShare news data"""
    return pd.DataFrame(
        [
            {
                "标题": "平安银行发布2024年业绩预告",
                "内容": "平安银行今日发布2024年业绩预告，预计净利润同比增长15%...",
                "链接": "https://finance.eastmoney.com/news/001.html",
                "来源": "东方财富",
                "发布时间": "2024-01-15 10:30:00",
            },
            {
                "标题": "平安银行获机构买入评级",
                "内容": "多家券商发布研报，给予平安银行买入评级...",
                "链接": "https://finance.eastmoney.com/news/002.html",
                "来源": "东方财富",
                "发布时间": "2024-01-14 15:20:00",
            },
            {
                "标题": "平安银行：数字化转型成效显著",
                "内容": "平安银行数字化转型持续推进，零售业务占比提升...",
                "链接": "https://finance.eastmoney.com/news/003.html",
                "来源": "证券时报",
                "发布时间": "2024-01-13 09:00:00",
            },
        ]
    )


@pytest.fixture
def mock_akshare_flash_data():
    """Mock AkShare flash news data"""
    return pd.DataFrame(
        [
            {
                "标题": "央行：保持流动性合理充裕",
                "内容": "中国人民银行今日表示，将继续实施稳健的货币政策...",
                "时间": "2024-01-15 10:00",
                "链接": "https://finance.sina.com.cn/001.html",
            },
            {
                "标题": "A股三大指数集体高开",
                "内容": "沪指高开0.5%，深成指高开0.6%，创业板指高开0.8%...",
                "时间": "2024-01-15 09:30",
                "链接": "https://finance.sina.com.cn/002.html",
            },
            {
                "标题": "平安银行涨停",
                "内容": "平安银行今日涨停，成交额超50亿元...",
                "时间": "2024-01-15 10:15",
                "链接": "https://finance.sina.com.cn/003.html",
            },
        ]
    )


@pytest.fixture
def akshare_news_provider():
    """Create AkShareNewsProvider instance"""
    return AkShareNewsProvider()


@pytest.fixture
def akshare_flash_provider():
    """Create AkShareFlashProvider instance"""
    return AkShareFlashProvider()


@pytest.fixture
def search_service_with_akshare():
    """Create SearchService with AkShare enabled"""
    return SearchService(use_akshare=True)


@pytest.fixture
def search_service_without_akshare():
    """Create SearchService with AkShare disabled"""
    return SearchService(use_akshare=False)


# ============================================
# AkShareNewsProvider Unit Tests
# ============================================


class TestAkShareNewsProvider:
    """AkShareNewsProvider tests"""

    def test_is_available_when_akshare_installed(self, akshare_news_provider):
        """Test is_available returns True when AkShare is installed"""
        assert akshare_news_provider.is_available is True

    def test_provider_name(self, akshare_news_provider):
        """Test provider name"""
        assert akshare_news_provider.name == "AkShare"

    @patch("akshare.stock_news_em")
    def test_search_a_stock_success(
        self, mock_news_em, akshare_news_provider, mock_akshare_news_data
    ):
        """Test A-share news search success"""
        mock_news_em.return_value = mock_akshare_news_data

        response = akshare_news_provider.search(
            "平安银行 000001 股票 最新消息", max_results=5
        )

        assert response.success is True
        assert response.provider == "AkShare"
        assert len(response.results) == 3
        assert "平安银行" in response.results[0].title
        mock_news_em.assert_called_once_with(symbol="000001")

    @patch("akshare.stock_news_em")
    def test_search_with_no_results(self, mock_news_em, akshare_news_provider):
        """Test search with no results"""
        mock_news_em.return_value = pd.DataFrame()

        response = akshare_news_provider.search(
            "平安银行 000001 股票 最新消息", max_results=5
        )

        assert response.success is False
        assert len(response.results) == 0
        assert "未找到" in response.error_message or "No" in response.error_message

    @patch("akshare.stock_news_em")
    def test_search_with_api_error(self, mock_news_em, akshare_news_provider):
        """Test API error handling"""
        mock_news_em.side_effect = Exception("Network error")

        response = akshare_news_provider.search(
            "平安银行 000001 股票 最新消息", max_results=5
        )

        assert response.success is False
        assert "Network error" in response.error_message

    def test_extract_stock_code_a_stock(self, akshare_news_provider):
        """Test extracting A-share code"""
        assert (
            akshare_news_provider._extract_stock_code("平安银行 000001 股票")
            == "000001"
        )
        assert akshare_news_provider._extract_stock_code("贵州茅台 600519") == "600519"
        assert (
            akshare_news_provider._extract_stock_code("宁德时代 300750 分析")
            == "300750"
        )

    def test_extract_stock_code_hk_stock(self, akshare_news_provider):
        """Test extracting HK stock code"""
        assert akshare_news_provider._extract_stock_code("腾讯控股 hk00700") == "00700"
        assert akshare_news_provider._extract_stock_code("小米集团 01810.HK") == "01810"

    def test_extract_stock_code_us_stock(self, akshare_news_provider):
        """Test extracting US stock code"""
        assert akshare_news_provider._extract_stock_code("Apple AAPL stock") == "AAPL"
        assert akshare_news_provider._extract_stock_code("Tesla TSLA news") == "TSLA"

    def test_extract_stock_code_no_code(self, akshare_news_provider):
        """Test no code returns None"""
        assert akshare_news_provider._extract_stock_code("没有股票代码的查询") is None

    @patch("akshare.stock_news_em")
    def test_max_results_limit(
        self, mock_news_em, akshare_news_provider, mock_akshare_news_data
    ):
        """Test max results limit"""
        mock_news_em.return_value = mock_akshare_news_data

        response = akshare_news_provider.search("平安银行 000001", max_results=2)

        assert len(response.results) == 2


# ============================================
# AkShareFlashProvider Unit Tests
# ============================================


class TestAkShareFlashProvider:
    """AkShareFlashProvider tests"""

    def test_is_available_when_akshare_installed(self, akshare_flash_provider):
        """Test is_available returns True when AkShare is installed"""
        assert akshare_flash_provider.is_available is True

    def test_provider_name(self, akshare_flash_provider):
        """Test provider name"""
        assert akshare_flash_provider.name == "AkShare-Flash"

    @patch("akshare.stock_info_global_sina")
    def test_search_flash_success(
        self, mock_flash, akshare_flash_provider, mock_akshare_flash_data
    ):
        """Test flash news search success"""
        mock_flash.return_value = mock_akshare_flash_data

        response = akshare_flash_provider.search("平安银行 最新消息", max_results=5)

        assert response.success is True
        assert response.provider == "AkShare-Flash"
        assert len(response.results) > 0

    @patch("akshare.stock_info_global_sina")
    def test_search_flash_with_cache(
        self, mock_flash, akshare_flash_provider, mock_akshare_flash_data
    ):
        """Test flash news caching mechanism"""
        mock_flash.return_value = mock_akshare_flash_data

        # Clear cache before test
        AkShareFlashProvider._flash_cache = {"data": None, "timestamp": 0, "ttl": 300}

        # First call, triggers API
        response1 = akshare_flash_provider.search("平安银行", max_results=5)
        assert mock_flash.call_count == 1

        # Second call, uses cache (within 5 minutes)
        response2 = akshare_flash_provider.search("平安银行", max_results=5)
        assert mock_flash.call_count == 1  # Not increased

        assert response1.success is True
        assert response2.success is True

    @patch("akshare.stock_info_global_sina")
    def test_search_flash_keyword_filter(
        self, mock_flash, akshare_flash_provider, mock_akshare_flash_data
    ):
        """Test flash news keyword filtering"""
        mock_flash.return_value = mock_akshare_flash_data

        response = akshare_flash_provider.search("平安银行", max_results=5)

        # Only flash news containing "平安银行" should be returned
        for result in response.results:
            assert "平安银行" in result.title or "平安银行" in result.snippet

    def test_extract_keywords(self, akshare_flash_provider):
        """Test keyword extraction"""
        keywords = akshare_flash_provider._extract_keywords(
            "平安银行 000001 股票 最新消息"
        )
        assert "平安银行" in keywords
        assert "000001" not in keywords  # Stock code filtered
        assert "股票" not in keywords  # Common word filtered

    def test_extract_keywords_empty(self, akshare_flash_provider):
        """Test empty keywords"""
        keywords = akshare_flash_provider._extract_keywords("000001 股票 最新 消息")
        assert len(keywords) == 0  # Only code and common words


# ============================================
# SearchService Integration Tests
# ============================================


class TestSearchServiceAkShareIntegration:
    """SearchService integration with AkShare tests"""

    def test_akshare_enabled_by_default(self):
        """Test AkShare is enabled by default"""
        service = SearchService()
        provider_names = [p.name for p in service._providers]
        assert "AkShare" in provider_names

    def test_akshare_can_be_disabled(self, search_service_without_akshare):
        """Test AkShare can be disabled"""
        provider_names = [p.name for p in search_service_without_akshare._providers]
        assert "AkShare" not in provider_names

    @patch("akshare.stock_news_em")
    def test_a_stock_uses_akshare_first(self, mock_news_em, mock_akshare_news_data):
        """Test A-share uses AkShare first"""
        mock_news_em.return_value = mock_akshare_news_data

        service = SearchService(tavily_keys=["mock_key"], use_akshare=True)

        response = service.search_stock_news("000001", "平安银行", max_results=5)

        assert response.success is True
        assert response.provider == "AkShare"
        mock_news_em.assert_called_once()

    @patch("akshare.stock_news_em")
    def test_hk_stock_fallback_to_other_providers(
        self, mock_news_em, search_service_with_akshare
    ):
        """Test HK stock does not use AkShare (fallback to other providers)"""
        # AkShare stock_news_em returns empty for HK stocks
        mock_news_em.return_value = pd.DataFrame()

        response = search_service_with_akshare.search_stock_news(
            "hk00700", "腾讯控股", max_results=5
        )

        # Without other engines configured, should fail
        assert response.success is False
        assert response.provider == "None"

    @patch("akshare.stock_news_em")
    def test_us_stock_fallback_to_other_providers(
        self, mock_news_em, search_service_with_akshare
    ):
        """Test US stock does not use AkShare (fallback to other providers)"""
        # AkShare stock_news_em returns empty for US stocks
        mock_news_em.return_value = pd.DataFrame()

        response = search_service_with_akshare.search_stock_news(
            "AAPL", "Apple", max_results=5
        )

        # Without other engines configured, should fail
        assert response.success is False
        assert response.provider == "None"

    @patch("akshare.stock_news_em")
    def test_cache_mechanism(self, mock_news_em, mock_akshare_news_data):
        """Test cache mechanism"""
        mock_news_em.return_value = mock_akshare_news_data

        service = SearchService(use_akshare=True)

        # First call
        response1 = service.search_stock_news("000001", "平安银行", max_results=5)
        assert mock_news_em.call_count == 1

        # Second call (same query), uses cache
        response2 = service.search_stock_news("000001", "平安银行", max_results=5)
        assert mock_news_em.call_count == 1  # Not increased

        assert response1.success is True
        assert response2.success is True


# ============================================
# Edge Cases Tests
# ============================================


class TestEdgeCases:
    """Edge cases tests"""

    def test_empty_stock_code(self, akshare_news_provider):
        """Test empty stock code"""
        response = akshare_news_provider.search("没有代码的查询", max_results=5)
        assert response.success is False

    def test_invalid_stock_code(self, akshare_news_provider):
        """Test invalid stock code"""
        response = akshare_news_provider.search("测试 1234567", max_results=5)
        # 7-digit code should not be recognized
        assert response.success is False

    @patch("akshare.stock_news_em")
    def test_malformed_response(self, mock_news_em, akshare_news_provider):
        """Test malformed response format"""
        # Return DataFrame with missing columns
        mock_news_em.return_value = pd.DataFrame([{"标题": "测试"}])

        response = akshare_news_provider.search("平安银行 000001", max_results=5)

        # Should handle gracefully without crashing
        assert response.success is True
        assert len(response.results) == 1


# ============================================
# Performance Tests
# ============================================


class TestPerformance:
    """Performance tests"""

    @patch("akshare.stock_news_em")
    def test_search_latency(
        self, mock_news_em, mock_akshare_news_data, akshare_news_provider
    ):
        """Test search latency"""
        mock_news_em.return_value = mock_akshare_news_data

        start_time = time.time()
        response = akshare_news_provider.search("平安银行 000001", max_results=5)
        elapsed = time.time() - start_time

        assert response.success is True
        assert elapsed < 5.0  # Should complete within 5 seconds

    @patch("akshare.stock_info_global_sina")
    def test_cache_improves_latency(
        self, mock_flash, mock_akshare_flash_data, akshare_flash_provider
    ):
        """Test cache improves performance"""
        mock_flash.return_value = mock_akshare_flash_data

        # First call (no cache)
        start1 = time.time()
        akshare_flash_provider.search("平安银行", max_results=5)
        elapsed1 = time.time() - start1

        # Second call (with cache)
        start2 = time.time()
        akshare_flash_provider.search("平安银行", max_results=5)
        elapsed2 = time.time() - start2

        # Cache should be faster or equal
        assert elapsed2 <= elapsed1
