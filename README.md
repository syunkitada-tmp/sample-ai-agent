# sample-ai-agent

## Bootstrap

```
$ uvx --from git+https://github.com/github/spec-kit.git specify init sample-ai-agent1
```

```
/specify Build an AI agent that collects and summarizes Japanese stock information.
```

## Japanese Stock Information AI Agent

An AI agent that collects, analyzes, and summarizes Japanese stock market information.

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Collect stock data:**
   ```bash
   python main.py collect --major
   ```

3. **Analyze stocks:**
   ```bash
   python main.py analyze --all
   ```

4. **Generate summary:**
   ```bash
   python main.py summarize --type daily
   ```

### CLI Commands

**Data Collection:**
- `collect --major` - Collect data for major Japanese stocks
- `collect --symbols 7203,6758,9984` - Collect specific stock symbols

**Analysis:**
- `analyze --all` - Analyze all stored stocks  
- `analyze --symbol 7203` - Analyze specific stock

**Summaries:**
- `summarize --type daily` - Generate daily market overview
- `summarize --type stock --symbol 7203` - Generate stock-specific summary

**Utilities:**
- `list-stocks` - Show all stored stocks
- `history` - Show recent summaries
- `health` - Check system status

### Implementation Status

✅ **Phase 1 Complete** - Basic functionality working
- Data collection from Yahoo Finance Japan
- SQLite storage with clean schema
- Technical analysis and risk assessment  
- Summary generation with insights
- Full CLI interface

📋 **Full Specification**: [`.specify/spec.md`](.specify/spec.md)  
📋 **Task Breakdown**: [`.specify/tasks.md`](.specify/tasks.md)

## Constitution

This project follows a simple constitution focused on rapid prototyping with good architecture. 

📋 **Full Constitution**: [`.specify/memory/constitution.md`](.specify/memory/constitution.md)

### 3 Core Principles
- **Working First**: Make it work, then make it better (NON-NEGOTIABLE)
- **Small Modules**: One module = One responsibility (NON-NEGOTIABLE)
- **Progressive Quality**: Prototype → Stabilization → Production