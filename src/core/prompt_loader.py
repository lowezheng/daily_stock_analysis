# -*- coding: utf-8 -*-
"""
Strategy Prompt Loader

Load analysis strategy prompts from external markdown files.
Supports fallback to built-in default strategy.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_STRATEGIES_DIR = Path(__file__).parent.parent.parent / "prompts" / "strategies"


@dataclass
class StrategyMetadata:
    """Strategy metadata from YAML frontmatter."""
    name: str = "未命名策略"
    version: str = "1.0"
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    output_format: str = "dashboard_v2"


@dataclass
class StrategyPrompt:
    """Loaded strategy prompt with metadata."""
    content: str
    metadata: StrategyMetadata
    source_path: Optional[Path] = None
    is_builtin: bool = False


class PromptLoader:
    """
    Strategy prompt loader with caching and fallback support.

    Usage:
        loader = PromptLoader()
        strategy = loader.load_strategy("trend")
        print(strategy.content)
    """

    _instance: Optional['PromptLoader'] = None

    def __new__(cls) -> 'PromptLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache: Dict[str, StrategyPrompt] = {}
        return cls._instance

    def load_strategy(
        self,
        strategy_name: Optional[str] = None,
        strategy_path: Optional[str] = None
    ) -> StrategyPrompt:
        """
        Load strategy prompt by name or path.

        Priority:
        1. strategy_path (if provided)
        2. strategy_name (lookup in strategies dir)
        3. "trend" (default built-in)

        Args:
            strategy_name: Strategy name (e.g., "trend", "value")
            strategy_path: Direct path to strategy file

        Returns:
            StrategyPrompt with content and metadata
        """
        cache_key = strategy_path or strategy_name or "default"
        if cache_key in self._cache:
            logger.debug(f"[PromptLoader] Cache hit: {cache_key}")
            return self._cache[cache_key]

        if strategy_path:
            result = self._load_from_path(Path(strategy_path))
            if result:
                self._cache[cache_key] = result
                return result
            logger.warning(f"[PromptLoader] Path not found: {strategy_path}, falling back")

        if strategy_name:
            result = self._load_by_name(strategy_name)
            if result:
                self._cache[cache_key] = result
                return result
            logger.warning(f"[PromptLoader] Strategy not found: {strategy_name}, falling back")

        result = self._load_default()
        self._cache[cache_key] = result
        return result

    def _load_from_path(self, path: Path) -> Optional[StrategyPrompt]:
        """Load strategy from a specific file path."""
        if not path.exists():
            return None
        try:
            content = path.read_text(encoding='utf-8')
            metadata, body = self._parse_frontmatter(content)
            return StrategyPrompt(
                content=body,
                metadata=metadata,
                source_path=path,
                is_builtin=False
            )
        except Exception as e:
            logger.error(f"[PromptLoader] Failed to load {path}: {e}")
            return None

    def _load_by_name(self, name: str) -> Optional[StrategyPrompt]:
        """Load strategy by name from strategies directory."""
        custom_path = DEFAULT_STRATEGIES_DIR / "custom" / f"{name}.md"
        if custom_path.exists():
            return self._load_from_path(custom_path)

        builtin_path = DEFAULT_STRATEGIES_DIR / f"{name}.md"
        if builtin_path.exists():
            return self._load_from_path(builtin_path)

        return None

    def _load_default(self) -> StrategyPrompt:
        """Load default strategy (trend.md or embedded fallback)."""
        result = self._load_by_name("trend")
        if result:
            result.is_builtin = True
            return result

        logger.warning("[PromptLoader] No strategy files found, using embedded default")
        return StrategyPrompt(
            content=self._get_embedded_default(),
            metadata=StrategyMetadata(
                name="趋势交易策略（内置）",
                version="2.0",
                description="内置默认策略，无外部文件依赖"
            ),
            source_path=None,
            is_builtin=True
        )

    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown content."""
        metadata = StrategyMetadata()

        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            try:
                import yaml
                yaml_content = match.group(1)
                body = match.group(2)
                data = yaml.safe_load(yaml_content) or {}

                metadata.name = data.get('name', metadata.name)
                metadata.version = data.get('version', metadata.version)
                metadata.description = data.get('description', metadata.description)
                metadata.author = data.get('author', metadata.author)
                metadata.tags = data.get('tags', [])
                metadata.output_format = data.get('output_format', metadata.output_format)

                return metadata, body.strip()
            except ImportError:
                logger.warning("[PromptLoader] PyYAML not installed, skipping frontmatter")
            except Exception as e:
                logger.warning(f"[PromptLoader] Failed to parse frontmatter: {e}")

        return metadata, content

    def _get_embedded_default(self) -> str:
        """Return embedded default SYSTEM_PROMPT."""
        return """你是一位专注于趋势交易的 A 股投资分析师，负责生成专业的【决策仪表盘】分析报告。

## 核心交易理念（必须严格遵守）

### 1. 严进策略（不追高）
- **绝对不追高**：当股价偏离 MA5 超过 5% 时，坚决不买入
- **乖离率公式**：(现价 - MA5) / MA5 × 100%
- 乖离率 < 2%：最佳买点区间
- 乖离率 2-5%：可小仓介入
- 乖离率 > 5%：严禁追高！直接判定为"观望"

### 2. 趋势交易（顺势而为）
- **多头排列必须条件**：MA5 > MA10 > MA20
- 只做多头排列的股票，空头排列坚决不碰

### 3. 买点偏好（回踩支撑）
- **最佳买点**：缩量回踩 MA5 获得支撑
- **次优买点**：回踩 MA10 获得支撑
- **观望情况**：跌破 MA20 时观望

请输出 JSON 格式的决策仪表盘。"""

    def list_strategies(self) -> List[Dict[str, Any]]:
        """List all available strategies."""
        strategies = []

        if DEFAULT_STRATEGIES_DIR.exists():
            for f in DEFAULT_STRATEGIES_DIR.glob("*.md"):
                if f.stem != "_default":
                    s = self._load_from_path(f)
                    if s:
                        strategies.append({
                            "name": f.stem,
                            "display_name": s.metadata.name,
                            "description": s.metadata.description,
                            "is_builtin": True
                        })

        custom_dir = DEFAULT_STRATEGIES_DIR / "custom"
        if custom_dir.exists():
            for f in custom_dir.glob("*.md"):
                s = self._load_from_path(f)
                if s:
                    strategies.append({
                        "name": f"custom/{f.stem}",
                        "display_name": s.metadata.name,
                        "description": s.metadata.description,
                        "is_builtin": False
                    })

        return strategies

    def clear_cache(self) -> None:
        """Clear the strategy cache for hot-reload."""
        self._cache.clear()


def get_prompt_loader() -> PromptLoader:
    """Get the singleton PromptLoader instance."""
    return PromptLoader()


def load_strategy_prompt(
    strategy_name: Optional[str] = None,
    strategy_path: Optional[str] = None
) -> str:
    """Convenience function to load strategy content directly."""
    loader = get_prompt_loader()
    strategy = loader.load_strategy(strategy_name, strategy_path)
    return strategy.content
