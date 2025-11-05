import ccxt
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime

# API Keys
MEXC_API_KEY = 'mx0vglpKet4seDX5h4'
MEXC_API_SECRET = '23d092bfc5c14e998b9203f33406a181'

BINANCE_API_KEY = 'oVTcJgLBoOOt8gMw0OOWsO7n0kRG73fPqGwkwvdBOACAmCRVADJJ8hRykbJGcaaR'
BINANCE_API_SECRET = 'bI2CVNjpiwLGVxqSyazdCrszBgEXpz51g0pmjS2HvY8KxQKbDMU8QZV46D14rU0W'

# Telegram настройки
TELEGRAM_BOT_TOKEN = '8012347683:AAEZESZJF8mgmNK74nyT4HcQk0zPcRrMcZQ'  # Получить у @BotFather
TELEGRAM_CHAT_ID = '-4678259306'  # Ваш chat ID

# Настройки
SPREAD_THRESHOLD = 0.0005  # 0.01% - порог для зеленого цвета
SYMBOL = 'APR/USDT:USDT'


def init_exchanges():
    """Инициализация бирж"""
    mexc = ccxt.mexc({
        'apiKey': MEXC_API_KEY,
        'secret': MEXC_API_SECRET,
        'timeout': 30000,
        'enableRateLimit': True
    })

    binance = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'timeout': 30000,
        'enableRateLimit': True
    })

    return mexc, binance


def format_percentage(value):
    """Форматирование в проценты"""
    return f"{value * 100:.4f}%"


def create_message(mexc_rate, binance_rate, spread):
    """Создание красивого сообщения для Telegram"""
    abs_spread = abs(spread)
    is_profitable = abs_spread >= SPREAD_THRESHOLD

    # Эмодзи и цвет
    if is_profitable:
        emoji = "🟢"
        status = "PROFITABLE"
    else:
        emoji = "🔴"
        status = "NOT PROFITABLE"

    # Определяем направление сделки
    if spread > 0:  # mexc > binance
        direction = "SHORT MEXC / LONG Binance"
    else:  # binance > mexc
        direction = "LONG MEXC / SHORT Binance"

    # Текущее время
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формируем сообщение с HTML разметкой
    message = f"""
{emoji} <b>{status}</b> {emoji}

📊 <b>Funding Rate Monitor</b>
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: <code>{SYMBOL}</code>
⏰ Time: <code>{timestamp}</code>

💹 <b>Rates:</b>
├ MEXC: <code>{format_percentage(mexc_rate)}</code>
├ Binance: <code>{format_percentage(binance_rate)}</code>
└ Spread: <b>{format_percentage(abs_spread)}</b>

📈 <b>Strategy:</b>
└ {direction}

💰 <b>Threshold:</b> {format_percentage(SPREAD_THRESHOLD)}
"""

    if is_profitable:
        message += f"\n✅ <b>Spread выше порога! Можно торговать!</b>"
    else:
        message += f"\n❌ Spread ниже порога. Ожидаем..."

    return message


async def send_telegram_message(message):
    """Отправка сообщения в Telegram"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )
        print("✓ Сообщение отправлено в Telegram")
    except Exception as e:
        print(f"✗ Ошибка отправки в Telegram: {e}")


async def main():
    """Основная функция"""
    try:
        # Инициализация бирж
        mexc, binance = init_exchanges()

        # Получение funding rates
        print("Получаем funding rates...")
        funding_mexc = mexc.fetch_funding_rate(SYMBOL)
        funding_binance = binance.fetch_funding_rate(SYMBOL)

        mexc_rate = funding_mexc['fundingRate']
        binance_rate = funding_binance['fundingRate']
        spread = mexc_rate - binance_rate

        # Вывод в консоль
        print(f"\nfundingRate mexc: {mexc_rate}")
        print(f"fundingRate binance: {binance_rate}")
        print(f"fundingRate spread: {spread}")
        print(f"Spread %: {format_percentage(abs(spread))}")

        # Создание и отправка сообщения
        message = create_message(mexc_rate, binance_rate, spread)
        await send_telegram_message(message)

    except Exception as e:
        error_message = f"❌ <b>ERROR</b>\n\n<code>{str(e)}</code>"
        print(f"Ошибка: {e}")
        try:
            await send_telegram_message(error_message)
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())