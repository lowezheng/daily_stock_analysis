#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AkShare News Interface Manual Test Script

Usage:
    python scripts/test_akshare_news.py              # Run all tests
    python scripts/test_akshare_news.py --news       # Test stock news only
    python scripts/test_akshare_news.py --flash      # Test flash news only
    python scripts/test_akshare_news.py --service    # Test SearchService integration
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_akshare_news():
    """Test individual stock news API"""
    print("\n" + "=" * 60)
    print("Testing AkShare Stock News API")
    print("=" * 60)

    try:
        import akshare as ak

        test_cases = [
            ("000001", "Ping An Bank"),
            ("600519", "Kweichow Moutai"),
            ("300750", "CATL"),
        ]

        for code, name in test_cases:
            print(f"\n>>> Testing {name}({code})")
            start_time = time.time()

            try:
                df = ak.stock_news_em(symbol=code)
                elapsed = time.time() - start_time

                if df is not None and not df.empty:
                    print(
                        f"    [OK] Retrieved {len(df)} news items (took {elapsed:.2f}s)"
                    )
                    print(f"    Latest: {df.iloc[0]['标题'][:40]}...")
                else:
                    print(f"    [WARN] Empty data returned")

            except Exception as e:
                print(f"    [FAIL] Error: {e}")

            time.sleep(1)  # Avoid rate limiting

    except ImportError:
        print("[FAIL] akshare not installed, run: pip install akshare")


def test_akshare_flash():
    """Test financial flash news API"""
    print("\n" + "=" * 60)
    print("Testing AkShare Financial Flash API")
    print("=" * 60)

    try:
        import akshare as ak

        print("\n>>> Fetching Sina financial flash news")
        start_time = time.time()

        try:
            df = ak.stock_info_global_sina()
            elapsed = time.time() - start_time

            if df is not None and not df.empty:
                print(
                    f"    [OK] Retrieved {len(df)} flash news items (took {elapsed:.2f}s)"
                )
                print("\n    Latest 3 flash news:")
                for i, row in df.head(3).iterrows():
                    title = row.get("标题", "")[:50]
                    time_str = row.get("时间", "")
                    print(f"    [{time_str}] {title}...")
            else:
                print(f"    [WARN] Empty data returned")

        except Exception as e:
            print(f"    [FAIL] Error: {e}")

    except ImportError:
        print("[FAIL] akshare not installed, run: pip install akshare")


def test_search_service_integration():
    """Test SearchService integration"""
    print("\n" + "=" * 60)
    print("Testing SearchService Integration")
    print("=" * 60)

    from src.search_service import (
        SearchService,
        AkShareNewsProvider,
        AkShareFlashProvider,
    )

    # 1. Test Provider initialization
    print("\n>>> Testing Provider initialization")

    news_provider = AkShareNewsProvider()
    flash_provider = AkShareFlashProvider()

    print(
        f"    AkShareNewsProvider: {'[OK] Available' if news_provider.is_available else '[FAIL] Unavailable'}"
    )
    print(
        f"    AkShareFlashProvider: {'[OK] Available' if flash_provider.is_available else '[FAIL] Unavailable'}"
    )

    # 2. Test SearchService initialization
    print("\n>>> Testing SearchService initialization")

    service_with_akshare = SearchService(use_akshare=True)
    service_without_akshare = SearchService(use_akshare=False)

    providers_with = [p.name for p in service_with_akshare._providers]
    providers_without = [p.name for p in service_without_akshare._providers]

    print(f"    With AkShare: {providers_with}")
    print(f"    Without AkShare: {providers_without}")

    assert "AkShare" in providers_with, "AkShare should be in providers"
    assert "AkShare" not in providers_without, "AkShare should not be in providers"
    print("    [OK] Initialization assertions passed")

    # 3. Test A-share search (priority AkShare)
    print("\n>>> Testing A-share search (should use AkShare first)")

    response = service_with_akshare.search_stock_news(
        "000001", "平安银行", max_results=5
    )

    if response.success:
        print(f"    [OK] Search successful")
        print(f"    Provider: {response.provider}")
        print(f"    Results: {len(response.results)}")
        if response.results:
            print(f"    First: {response.results[0].title[:40]}...")
    else:
        print(f"    [FAIL] Search failed: {response.error_message}")

    # 4. Test HK stock search (should fallback)
    print("\n>>> Testing HK stock search (should fallback)")

    response = service_with_akshare.search_stock_news(
        "hk00700", "Tencent", max_results=5
    )

    if response.success:
        print(f"    [OK] Search successful (Provider: {response.provider})")
    else:
        print(
            f"    [WARN] No available engine (expected behavior, no other API keys configured)"
        )

    # 5. Test AkShare disabled
    print("\n>>> Testing with AkShare disabled")

    response = service_without_akshare.search_stock_news(
        "000001", "平安银行", max_results=5
    )

    if response.success:
        print(f"    [OK] Search successful (Provider: {response.provider})")
    else:
        print(
            f"    [WARN] No available engine (expected behavior, AkShare disabled and no other keys)"
        )

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="AkShare News Interface Tests")
    parser.add_argument("--news", action="store_true", help="Test stock news only")
    parser.add_argument("--flash", action="store_true", help="Test flash news only")
    parser.add_argument(
        "--service", action="store_true", help="Test SearchService integration"
    )

    args = parser.parse_args()

    # If no specific option, run all tests
    run_all = not (args.news or args.flash or args.service)

    if run_all or args.news:
        test_akshare_news()

    if run_all or args.flash:
        test_akshare_flash()

    if run_all or args.service:
        test_search_service_integration()


if __name__ == "__main__":
    main()
