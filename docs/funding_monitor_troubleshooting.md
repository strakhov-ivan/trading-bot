# Troubleshooting и расширенные примеры

## Оглавление
1. [Частые проблемы и решения](#частые-проблемы-и-решения)
2. [Логирование и отладка](#логирование-и-отладка)
3. [Расширения функционала](#расширения-функционала)
4. [Оптимизация производительности](#оптимизация-производительности)

---

## Частые проблемы и решения

### 1. Ошибка аутентификации

**Проблема**:
```
AuthenticationError: Invalid API-key, IP, or permissions for action
```

**Решения**:
- ✅ Проверьте правильность API ключей
- ✅ Убедитесь, что IP адрес добавлен в whitelist
- ✅ Проверьте права доступа API ключа (нужен доступ к futures)
- ✅ Убедитесь, что ключи не содержат лишних пробелов

**Проверка ключей**:
```python
# Добавьте в начало main()
print(f"MEXC API Key length: {len(MEXC_API_KEY)}")
print(f"MEXC API Key starts with: {MEXC_API_KEY[:5]}...")
print(f"Binance API Key length: {len(BINANCE_API_KEY)}")
```

---

### 2. Символ не найден

**Проблема**:
```
ExchangeError: {"code":-1121,"msg":"Invalid symbol."}
```

**Решения**:
- ✅ Проверьте формат символа: `'APR/USDT:USDT'` для фьючерсов
- ✅ Убедитесь, что символ торгуется на обеих биржах
- ✅ Используйте `exchange.load_markets()` для проверки доступных символов

**Проверка доступных символов**:
```python
def check_symbol_availability():
    mexc, binance = init_exchanges()
    
    # Загружаем рынки
    mexc.load_markets()
    binance.load_markets()
    
    # Проверяем наличие символа
    symbol = 'APR/USDT:USDT'
    
    print(f"MEXC has {symbol}: {symbol in mexc.markets}")
    print(f"Binance has {symbol}: {symbol in binance.markets}")
    
    # Показываем похожие символы
    mexc_symbols = [s for s in mexc.markets if 'APR' in s]
    binance_symbols = [s for s in binance.markets if 'APR' in s]
    
    print(f"\nMEXC symbols with APR: {mexc_symbols}")
    print(f"Binance symbols with APR: {binance_symbols}")

# Запуск проверки
check_symbol_availability()
```

---

### 3. Timeout ошибки

**Проблема**:
```
RequestTimeout: Request timeout
```

**Решения**:
- ✅ Увеличьте timeout в настройках биржи
- ✅ Проверьте интернет-соединение
- ✅ Используйте retry механизм

**Пример с retry**:
```python
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import ccxt

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(ccxt.RequestTimeout)
)
def fetch_funding_rate_with_retry(exchange, symbol):
    """Получение funding rate с повторными попытками"""
    print(f"Attempting to fetch funding rate for {symbol}...")
    return exchange.fetch_funding_rate(symbol)

# Использование в main()
async def main():
    try:
        mexc, binance = init_exchanges()
        
        # Используем функцию с retry
        funding_mexc = fetch_funding_rate_with_retry(mexc, SYMBOL)
        funding_binance = fetch_funding_rate_with_retry(binance, SYMBOL)
        
        # ... остальной код
    except Exception as e:
        print(f"Failed after retries: {e}")
```

---

### 4. Rate Limit ошибки

**Проблема**:
```
RateLimitExceeded: Too many requests
```

**Решения**:
- ✅ Убедитесь, что `enableRateLimit=True`
- ✅ Увеличьте интервал между запросами
- ✅ Используйте `exchange.rateLimit` для проверки лимитов

**Добавление задержки**:
```python
import time

async def main():
    mexc, binance = init_exchanges()
    
    # Получаем данные с MEXC
    funding_mexc = mexc.fetch_funding_rate(SYMBOL)
    
    # Задержка перед следующим запросом
    time.sleep(1)
    
    # Получаем данные с Binance
    funding_binance = binance.fetch_funding_rate(SYMBOL)
```

---

### 5. Telegram ошибки

**Проблема**:
```
telegram.error.Unauthorized: Forbidden: bot was blocked by the user
```

**Решения**:
- ✅ Проверьте, что бот не заблокирован
- ✅ Убедитесь, что CHAT_ID правильный
- ✅ Проверьте, что бот добавлен в группу (если используется группа)
- ✅ Для групп CHAT_ID должен начинаться с `-`

**Проверка Telegram подключения**:
```python
async def test_telegram():
    """Тестирование подключения к Telegram"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"Bot username: @{bot_info.username}")
        print(f"Bot name: {bot_info.first_name}")
        
        # Пробуем отправить тестовое сообщение
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🧪 Test message from Funding Monitor"
        )
        print("✓ Test message sent successfully")
        
    except Exception as e:
        print(f"✗ Telegram test failed: {e}")

# Запуск теста
asyncio.run(test_telegram())
```

---

### 6. Проблемы с форматированием HTML

**Проблема**:
```
telegram.error.BadRequest: Can't parse entities
```

**Решение**: Экранируйте специальные символы в HTML

```python
import html

def escape_html(text):
    """Экранирование HTML символов"""
    return html.escape(str(text))

def create_message_safe(mexc_rate, binance_rate, spread):
    """Безопасное создание сообщения с экранированием"""
    # Экранируем значения
    symbol_safe = escape_html(SYMBOL)
    
    message = f"""
🟢 <b>PROFITABLE</b> 🟢

📊 <b>Funding Rate Monitor</b>
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: <code>{symbol_safe}</code>
⏰ Time: <code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</code>
"""
    return message
```

---

## Логирование и отладка

### Настройка подробного логирования

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Настройка системы логирования"""
    # Создаем логгер
    logger = logging.getLogger('funding_monitor')
    logger.setLevel(logging.DEBUG)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Хендлер для файла (с ротацией)
    file_handler = RotatingFileHandler(
        'funding_monitor.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем хендлеры
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Использование в коде
logger = setup_logging()

async def main():
    try:
        logger.info("Starting funding rate monitor")
        
        mexc, binance = init_exchanges()
        logger.debug("Exchanges initialized")
        
        logger.info(f"Fetching funding rate for {SYMBOL}")
        funding_mexc = mexc.fetch_funding_rate(SYMBOL)
        logger.debug(f"MEXC response: {funding_mexc}")
        
        funding_binance = binance.fetch_funding_rate(SYMBOL)
        logger.debug(f"Binance response: {funding_binance}")
        
        mexc_rate = funding_mexc['fundingRate']
        binance_rate = funding_binance['fundingRate']
        spread = mexc_rate - binance_rate
        
        logger.info(f"MEXC: {mexc_rate}, Binance: {binance_rate}, Spread: {spread}")
        
        if abs(spread) >= SPREAD_THRESHOLD:
            logger.warning(f"Profitable opportunity detected! Spread: {abs(spread)}")
        else:
            logger.info(f"Spread below threshold: {abs(spread)} < {SPREAD_THRESHOLD}")
        
        message = create_message(mexc_rate, binance_rate, spread)
        await send_telegram_message(message)
        logger.info("Telegram notification sent")
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
```

---

## Расширения функционала

### 1. Мониторинг нескольких торговых пар

```python
# Конфигурация
SYMBOLS = [
    'APR/USDT:USDT',
    'BTC/USDT:USDT',
    'ETH/USDT:USDT',
    'SOL/USDT:USDT'
]

async def monitor_multiple_symbols():
    """Мониторинг нескольких символов"""
    mexc, binance = init_exchanges()
    
    results = []
    
    for symbol in SYMBOLS:
        try:
            logger.info(f"Checking {symbol}")
            
            funding_mexc = mexc.fetch_funding_rate(symbol)
            funding_binance = binance.fetch_funding_rate(symbol)
            
            mexc_rate = funding_mexc['fundingRate']
            binance_rate = funding_binance['fundingRate']
            spread = mexc_rate - binance_rate
            
            results.append({
                'symbol': symbol,
                'mexc_rate': mexc_rate,
                'binance_rate': binance_rate,
                'spread': spread,
                'is_profitable': abs(spread) >= SPREAD_THRESHOLD
            })
            
            # Задержка между запросами
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error checking {symbol}: {e}")
            continue
    
    # Отправляем сводный отчет
    await send_summary_report(results)
    
    return results

async def send_summary_report(results):
    """Отправка сводного отчета по всем символам"""
    profitable = [r for r in results if r['is_profitable']]
    
    message = f"""
📊 <b>Multi-Symbol Funding Rate Report</b>
━━━━━━━━━━━━━━━━━━━━
⏰ Time: <code>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</code>

🔍 Checked: {len(results)} symbols
🟢 Profitable: {len(profitable)} symbols

"""
    
    if profitable:
        message += "<b>Profitable Opportunities:</b>\n"
        for r in profitable:
            message += f"\n🪙 {r['symbol']}\n"
            message += f"├ Spread: <b>{format_percentage(abs(r['spread']))}</b>\n"
            if r['spread'] > 0:
                message += f"└ Strategy: SHORT MEXC / LONG Binance\n"
            else:
                message += f"└ Strategy: LONG MEXC / SHORT Binance\n"
    else:
        message += "\n❌ No profitable opportunities at the moment"
    
    await send_telegram_message(message)
```

---

### 2. Сохранение истории в базу данных

```python
import sqlite3
from datetime import datetime

def init_database():
    """Инициализация базы данных"""
    conn = sqlite3.connect('funding_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funding_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            mexc_rate REAL NOT NULL,
            binance_rate REAL NOT NULL,
            spread REAL NOT NULL,
            is_profitable BOOLEAN NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_to_database(symbol, mexc_rate, binance_rate, spread, is_profitable):
    """Сохранение данных в базу"""
    conn = sqlite3.connect('funding_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO funding_rates 
        (symbol, mexc_rate, binance_rate, spread, is_profitable)
        VALUES (?, ?, ?, ?, ?)
    ''', (symbol, mexc_rate, binance_rate, spread, is_profitable))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Data saved to database for {symbol}")

def get_history(symbol, hours=24):
    """Получение истории за последние N часов"""
    conn = sqlite3.connect('funding_history.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, mexc_rate, binance_rate, spread, is_profitable
        FROM funding_rates
        WHERE symbol = ?
        AND timestamp >= datetime('now', '-' || ? || ' hours')
        ORDER BY timestamp DESC
    ''', (symbol, hours))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

# Использование в main()
async def main():
    # Инициализируем БД при первом запуске
    init_database()
    
    try:
        mexc, binance = init_exchanges()
        
        funding_mexc = mexc.fetch_funding_rate(SYMBOL)
        funding_binance = binance.fetch_funding_rate(SYMBOL)
        
        mexc_rate = funding_mexc['fundingRate']
        binance_rate = funding_binance['fundingRate']
        spread = mexc_rate - binance_rate
        is_profitable = abs(spread) >= SPREAD_THRESHOLD
        
        # Сохраняем в базу
        save_to_database(SYMBOL, mexc_rate, binance_rate, spread, is_profitable)
        
        # Остальной код...
        
    except Exception as e:
        logger.error(f"Error: {e}")
```

---

### 3. Визуализация данных

```python
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def plot_spread_history(symbol, hours=24):
    """Построение графика истории спреда"""
    # Получаем данные из БД
    history = get_history(symbol, hours)
    
    if not history:
        print("No data available")
        return
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(history, columns=[
        'timestamp', 'mexc_rate', 'binance_rate', 'spread', 'is_profitable'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Создаем график
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # График 1: Funding rates
    ax1.plot(df['timestamp'], df['mexc_rate'] * 100, label='MEXC', marker='o')
    ax1.plot(df['timestamp'], df['binance_rate'] * 100, label='Binance', marker='s')
    ax1.set_ylabel('Funding Rate (%)')
    ax1.set_title(f'Funding Rates History - {symbol}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # График 2: Spread
    colors = ['green' if p else 'red' for p in df['is_profitable']]
    ax2.bar(df['timestamp'], df['spread'] * 100, color=colors, alpha=0.6)
    ax2.axhline(y=SPREAD_THRESHOLD * 100, color='orange', linestyle='--', 
                label=f'Threshold ({SPREAD_THRESHOLD*100}%)')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Spread (%)')
    ax2.set_title('Spread History')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'spread_history_{symbol.replace("/", "_")}.png', dpi=150)
    print(f"Chart saved to spread_history_{symbol.replace('/', '_')}.png")

# Использование
plot_spread_history('APR/USDT:USDT', hours=24)
```

---

### 4. Отправка графиков в Telegram

```python
async def send_chart_to_telegram(symbol):
    """Создание и отправка графика в Telegram"""
    # Создаем график
    plot_spread_history(symbol, hours=24)
    
    # Отправляем в Telegram
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    chart_path = f'spread_history_{symbol.replace("/", "_")}.png'
    
    with open(chart_path, 'rb') as photo:
        await bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=photo,
            caption=f"📊 Spread history for {symbol} (last 24 hours)"
        )
    
    logger.info(f"Chart sent to Telegram for {symbol}")
```

---

### 5. Расчет статистики

```python
def calculate_statistics(symbol, hours=24):
    """Расчет статистики по символу"""
    history = get_history(symbol, hours)
    
    if not history:
        return None
    
    df = pd.DataFrame(history, columns=[
        'timestamp', 'mexc_rate', 'binance_rate', 'spread', 'is_profitable'
    ])
    
    stats = {
        'symbol': symbol,
        'period_hours': hours,
        'total_checks': len(df),
        'profitable_count': df['is_profitable'].sum(),
        'profitable_percentage': (df['is_profitable'].sum() / len(df)) * 100,
        'avg_spread': df['spread'].mean(),
        'max_spread': df['spread'].max(),
        'min_spread': df['spread'].min(),
        'avg_mexc_rate': df['mexc_rate'].mean(),
        'avg_binance_rate': df['binance_rate'].mean()
    }
    
    return stats

async def send_statistics_report(symbol):
    """Отправка статистического отчета"""
    stats = calculate_statistics(symbol, hours=24)
    
    if not stats:
        await send_telegram_message("❌ No statistics available")
        return
    
    message = f"""
📈 <b>Statistics Report</b>
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: <code>{stats['symbol']}</code>
⏰ Period: {stats['period_hours']} hours

📊 <b>Checks:</b>
├ Total: {stats['total_checks']}
├ Profitable: {stats['profitable_count']}
└ Success Rate: <b>{stats['profitable_percentage']:.1f}%</b>

💹 <b>Spread Statistics:</b>
├ Average: {format_percentage(stats['avg_spread'])}
├ Maximum: {format_percentage(stats['max_spread'])}
└ Minimum: {format_percentage(stats['min_spread'])}

📉 <b>Average Rates:</b>
├ MEXC: {format_percentage(stats['avg_mexc_rate'])}
└ Binance: {format_percentage(stats['avg_binance_rate'])}
"""
    
    await send_telegram_message(message)
```

---

## Оптимизация производительности

### 1. Асинхронные запросы к биржам

```python
import aiohttp
import asyncio

async def fetch_funding_rates_async(mexc, binance, symbol):
    """Асинхронное получение funding rates с обеих бирж"""
    # Создаем задачи для параллельного выполнения
    tasks = [
        asyncio.create_task(asyncio.to_thread(mexc.fetch_funding_rate, symbol)),
        asyncio.create_task(asyncio.to_thread(binance.fetch_funding_rate, symbol))
    ]
    
    # Ждем выполнения обеих задач
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Проверяем на ошибки
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            exchange_name = 'MEXC' if i == 0 else 'Binance'
            logger.error(f"Error fetching from {exchange_name}: {result}")
            raise result
    
    return results[0], results[1]

# Использование
async def main():
    mexc, binance = init_exchanges()
    
    # Параллельное получение данных
    funding_mexc, funding_binance = await fetch_funding_rates_async(
        mexc, binance, SYMBOL
    )
    
    # Остальной код...
```

---

### 2. Кэширование результатов

```python
from functools import lru_cache
from datetime import datetime, timedelta

class FundingRateCache:
    """Кэш для funding rates"""
    def __init__(self, ttl_seconds=60):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, exchange, symbol):
        """Получить из кэша"""
        key = f"{exchange}_{symbol}"
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.debug(f"Cache hit for {key}")
                return data
        return None
    
    def set(self, exchange, symbol, data):
        """Сохранить в кэш"""
        key = f"{exchange}_{symbol}"
        self.cache[key] = (data, datetime.now())
        logger.debug(f"Cached {key}")

# Использование
cache = FundingRateCache(ttl_seconds=60)

async def main():
    mexc, binance = init_exchanges()
    
    # Пробуем получить из кэша
    cached_mexc = cache.get('mexc', SYMBOL)
    if cached_mexc:
        funding_mexc = cached_mexc
    else:
        funding_mexc = mexc.fetch_funding_rate(SYMBOL)
        cache.set('mexc', SYMBOL, funding_mexc)
    
    # Аналогично для Binance
    cached_binance = cache.get('binance', SYMBOL)
    if cached_binance:
        funding_binance = cached_binance
    else:
        funding_binance = binance.fetch_funding_rate(SYMBOL)
        cache.set('binance', SYMBOL, funding_binance)
    
    # Остальной код...
```

---

## Заключение

Эти расширения и оптимизации помогут сделать Funding Rate Monitor более надежным, функциональным и производительным. Выбирайте те функции, которые соответствуют вашим потребностям.
