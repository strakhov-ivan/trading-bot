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


def calculate_profit(mexc_rate, binance_rate, mexc_position, binance_position):
    """
    Расчет реальной прибыли с учетом направления позиций
    
    Логика:
    - Если FR положительная (+): LONG платит, SHORT получает
    - Если FR отрицательная (-): SHORT платит, LONG получает
    """
    # Рассчитываем P&L на MEXC
    if mexc_position == 'SHORT':
        mexc_pnl = mexc_rate if mexc_rate > 0 else -mexc_rate
    else:  # LONG
        mexc_pnl = -mexc_rate if mexc_rate > 0 else mexc_rate
    
    # Рассчитываем P&L на Binance
    if binance_position == 'SHORT':
        binance_pnl = binance_rate if binance_rate > 0 else -binance_rate
    else:  # LONG
        binance_pnl = -binance_rate if binance_rate > 0 else binance_rate
    
    # Общая прибыль
    total_profit = mexc_pnl + binance_pnl
    
    return total_profit, mexc_pnl, binance_pnl


def create_message(mexc_rate, binance_rate, spread):
    """Создание красивого сообщения для Telegram с учетом направления позиций"""
    
    # Определяем оптимальное направление сделки
    if spread > 0:  # mexc > binance
        mexc_position = "SHORT"
        binance_position = "LONG"
    else:  # binance > mexc
        mexc_position = "LONG"
        binance_position = "SHORT"
    
    # Рассчитываем реальную прибыль
    total_profit, mexc_pnl, binance_pnl = calculate_profit(
        mexc_rate, binance_rate, mexc_position, binance_position
    )
    
    # Проверяем прибыльность
    is_profitable = abs(total_profit) >= SPREAD_THRESHOLD
    
    # Эмодзи и статус
    if is_profitable:
        emoji = "🟢"
        status = "PROFITABLE"
    else:
        emoji = "🔴"
        status = "NOT PROFITABLE"
    
    # Текущее время
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Определяем знак для отображения
    mexc_sign = "+" if mexc_pnl > 0 else ""
    binance_sign = "+" if binance_pnl > 0 else ""
    profit_sign = "+" if total_profit > 0 else ""
    
    # Формируем сообщение с HTML разметкой
    message = f"""
{emoji} <b>{status}</b> {emoji}

📊 <b>Funding Rate Monitor</b>
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: <code>{SYMBOL}</code>
⏰ Time: <code>{timestamp}</code>

💹 <b>Funding Rates:</b>
├ MEXC: <code>{format_percentage(mexc_rate)}</code>
└ Binance: <code>{format_percentage(binance_rate)}</code>

📈 <b>Recommended Strategy:</b>
├ MEXC: <b>{mexc_position}</b>
└ Binance: <b>{binance_position}</b>

💰 <b>Profit Breakdown:</b>
├ MEXC {mexc_position}: <code>{mexc_sign}{format_percentage(mexc_pnl)}</code>
├ Binance {binance_position}: <code>{binance_sign}{format_percentage(binance_pnl)}</code>
└ <b>Total Profit: {profit_sign}{format_percentage(abs(total_profit))}</b>

🎯 <b>Threshold:</b> {format_percentage(SPREAD_THRESHOLD)}
"""
    
    if is_profitable:
        message += f"\n✅ <b>Прибыль выше порога! Можно торговать!</b>"
        # Добавляем пример расчета на $10,000
        profit_10k = abs(total_profit) * 10000
        profit_daily = profit_10k * 3  # 3 раза в день (каждые 8 часов)
        profit_monthly = profit_daily * 30
        message += f"\n\n💵 <b>Пример на $10,000:</b>"
        message += f"\n├ За 8 часов: <code>${profit_10k:.2f}</code>"
        message += f"\n├ В день: <code>${profit_daily:.2f}</code>"
        message += f"\n└ В месяц: <code>${profit_monthly:.2f}</code>"
    else:
        message += f"\n❌ Прибыль ниже порога. Ожидаем..."
    
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

        # Определяем оптимальные позиции
        if spread > 0:
            mexc_pos = "SHORT"
            binance_pos = "LONG"
        else:
            mexc_pos = "LONG"
            binance_pos = "SHORT"
        
        # Рассчитываем прибыль
        total_profit, mexc_pnl, binance_pnl = calculate_profit(
            mexc_rate, binance_rate, mexc_pos, binance_pos
        )
        
        # Вывод в консоль
        print(f"\n" + "="*50)
        print(f"Funding Rates:")
        print(f"  MEXC:    {format_percentage(mexc_rate)}")
        print(f"  Binance: {format_percentage(binance_rate)}")
        print(f"  Spread:  {format_percentage(spread)}")
        print(f"\nRecommended Positions:")
        print(f"  MEXC:    {mexc_pos}")
        print(f"  Binance: {binance_pos}")
        print(f"\nProfit Breakdown:")
        print(f"  MEXC {mexc_pos}:    {'+' if mexc_pnl > 0 else ''}{format_percentage(mexc_pnl)}")
        print(f"  Binance {binance_pos}: {'+' if binance_pnl > 0 else ''}{format_percentage(binance_pnl)}")
        print(f"  Total Profit: {'+' if total_profit > 0 else ''}{format_percentage(abs(total_profit))}")
        print(f"\nProfitable: {'✅ YES' if abs(total_profit) >= SPREAD_THRESHOLD else '❌ NO'}")
        print("="*50)

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