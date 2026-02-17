# AGENTS.md - Bot Module (bot/)

This module provides chatbot command handling for multiple platforms.

## Module Overview

The `bot/` directory implements bot functionality for triggering stock analysis via chat commands:
- Unified message/response models (`models.py`)
- Command dispatcher (`dispatcher.py`)
- Command handlers (`commands/`)
- Platform adapters (`platforms/`)
- Webhook handler (`handler.py`)

### Supported Platforms

| Platform | Mode | File |
|----------|------|------|
| Feishu (飞书) | Webhook + Stream | `feishu_stream.py` |
| DingTalk (钉钉) | Webhook + Stream | `dingtalk.py`, `dingtalk_stream.py` |
| WeCom (企业微信) | Webhook | (planned) |
| Telegram | Webhook | (via notification) |
| Discord | Bot | `discord.py` |

### Supported Commands

| Command | Description |
|---------|-------------|
| `/analyze <code>` | Analyze a specific stock |
| `/market` | Market review |
| `/batch` | Batch analyze watchlist |
| `/help` | Show help message |
| `/status` | System status |

## Build/Lint/Test Commands

```bash
# Syntax check
python -m py_compile bot/*.py bot/commands/*.py bot/platforms/*.py

# Lint
flake8 bot/ --max-line-length=120

# Run with bot support
python main.py --serve

# Test bot dispatcher
python -c "from bot.dispatcher import get_dispatcher; d = get_dispatcher(); print(d)"
```

## Code Style Guidelines

### Command Handler Pattern

```python
from bot.commands.base import CommandHandler
from bot.models import BotMessage, BotResponse

class AnalyzeCommand(CommandHandler):
    """Handle /analyze command."""
    
    @property
    def command(self) -> str:
        return "analyze"
    
    @property
    def description(self) -> str:
        return "Analyze a stock"
    
    async def handle(self, message: BotMessage) -> BotResponse:
        # Parse stock code from message
        code = self._parse_code(message.text)
        if not code:
            return BotResponse(text="Please provide a stock code")
        
        # Trigger analysis
        result = await self._analyze(code)
        return BotResponse(text=result)
```

### Platform Adapter Pattern

```python
from bot.platforms.base import PlatformAdapter

class FeishuAdapter(PlatformAdapter):
    """Feishu platform adapter."""
    
    async def handle_webhook(self, request: Request) -> Response:
        """Handle incoming webhook request."""
        message = self._parse_request(request)
        response = await self.dispatcher.dispatch(message)
        return self._format_response(response)
```

### Message Models

```python
from bot.models import BotMessage, BotResponse, ChatType

message = BotMessage(
    platform="feishu",
    chat_type=ChatType.GROUP,
    user_id="user123",
    text="/analyze 600519",
    raw_data={...}
)

response = BotResponse(
    text="Analysis result...",
    mention_user=False
)
```

### Naming Conventions

- Command handlers: `PascalCase` + `Command` (e.g., `AnalyzeCommand`)
- Platform adapters: `PascalCase` + `Adapter` (e.g., `FeishuAdapter`)
- Command files: `snake_case.py` (e.g., `analyze.py`, `market.py`)

## Platform Configuration

### Environment Variables

| Variable | Platform | Description |
|----------|----------|-------------|
| `FEISHU_APP_ID` | Feishu | App ID |
| `FEISHU_APP_SECRET` | Feishu | App Secret |
| `FEISHU_STREAM_ENABLED` | Feishu | Enable Stream mode |
| `DINGTALK_APP_KEY` | DingTalk | App Key |
| `DINGTALK_APP_SECRET` | DingTalk | App Secret |
| `DINGTALK_STREAM_ENABLED` | DingTalk | Enable Stream mode |
| `DISCORD_BOT_TOKEN` | Discord | Bot Token |
| `DISCORD_MAIN_CHANNEL_ID` | Discord | Main channel ID |

### Webhook vs Stream Mode

- **Webhook mode**: Requires public IP, receives events via HTTP POST
- **Stream mode**: Uses long polling, no public IP required

## Rate Limiting

Bot commands are rate-limited per user:
- `BOT_RATE_LIMIT_REQUESTS`: Max requests per window (default: 10)
- `BOT_RATE_LIMIT_WINDOW`: Window in seconds (default: 60)

## Module Relationships

```
main.py
    └── bot/__init__.py
            ├── bot/dispatcher.py (CommandDispatcher)
            │       └── bot/commands/*.py (command handlers)
            ├── bot/platforms/*.py (platform adapters)
            └── bot/handler.py (webhook handlers)
                    └── api/v1/endpoints/bot.py (FastAPI routes)
```

## Dependencies

- `lark-oapi` - Feishu SDK
- `dingtalk-stream` - DingTalk Stream SDK
- `discord.py` - Discord bot library

## Adding New Commands

1. Create file in `bot/commands/` (e.g., `newcmd.py`)
2. Extend `CommandHandler` base class
3. Implement `handle()` method
4. Register in `bot/commands/__init__.py`

## Adding New Platforms

1. Create file in `bot/platforms/` (e.g., `newplatform.py`)
2. Extend `PlatformAdapter` base class
3. Implement webhook handling
4. Register in `bot/platforms/__init__.py`
