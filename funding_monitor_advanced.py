import ccxt
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime, timedelta
import pytz

# API Keys
MEXC_API_KEY = 'mx0vglpKet4seDX5h4'
MEXC_API_SECRET = '23d092bfc5c14e998b9203f33406a181'

BINANCE_API_KEY = 'oVTcJgLBoOOt8gMw0OOWsO7n0kRG73fPqGwkwvdBOACAmCRVADJJ8hRykbJGcaaR'
BINANCE_API_SECRET = 'bI2CVNjpiwLGVxqSyazdCrszBgEXpz51g0pmjS2HvY8KxQKbDMU8QZV46D14rU0W'

# Telegram настройки
TELEGRAM_BOT_TOKEN = '8012347683:AAEZESZJF8mgmNK74nyT4HcQk0zPcRrMcZQ'
TELEGRAM_CHAT_ID = '-4678259306'

# Настройки
SPREAD_THRESHOLD = 0.0005  # 0.05% - порог для зеленого цвета
SYMBOL = 'APR/USDT:USDT'
CHECK_POSITIONS = True  # Проверять реальные позиции


def init_exchanges():
    """Инициализация бирж"""
    mexc = ccxt.mexc({
        'apiKey': MEXC_API_KEY,
        'secret': MEXC_API_SECRET,
        'timeout': 30000,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',  # Для фьючерсов
        }
    })

    binance = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'timeout': 30000,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',  # Для фьючерсов
        }
    })

    return mexc, binance


def format_percentage(value):
    """Форматирование в проценты"""
    return f"{value * 100:.4f}%"


def get_next_funding_time():
    """Рассчитать время до следующего funding"""
    now = datetime.now(pytz.UTC)
    
    # Funding происходит в 00:00, 08:00, 16:00 UTC
    funding_hours = [0, 8, 16]
    
    # Находим следующее время funding
    current_hour = now.hour
    next_funding_hour = None
    
    for hour in funding_hours:
        if hour > current_hour:
            next_funding_hour = hour
            break
    
    if next_funding_hour is None:
        # Следующий funding завтра в 00:00
        next_funding = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        next_funding = now.replace(hour=next_funding_hour, minute=0, second=0, microsecond=0)
    
    time_until_funding = next_funding - now
    hours = int(time_until_funding.total_seconds() // 3600)
    minutes = int((time_until_funding.total_seconds() % 3600) // 60)
    
    return next_funding, hours, minutes


def get_positions(exchange, symbol):
    """
    Получить открытые позиции по символу
    Возвращает: (side, size) где side = 'LONG' или 'SHORT' или None
    """
    try:
        positions = exchange.fetch_positions([symbol])
        
        for position in positions:
            if position['symbol'] == symbol:
                contracts = float(position.get('contracts', 0))
                
                if contracts == 0:
                    continue
                
                side = position.get('side', '').upper()
                
                # Нормализуем side
                if side in ['LONG', 'BUY']:
                    return 'LONG', abs(contracts)
                elif side in ['SHORT', 'SELL']:
                    return 'SHORT', abs(contracts)
        
        return None, 0
    
    except Exception as e:
        print(f"Ошибка получения позиций: {e}")
        return None, 0


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


def analyze_positions(mexc_rate, binance_rate, mexc_pos, binance_pos, mexc_size, binance_size):
    """
    Анализ текущих позиций и рекомендации
    """
    # Определяем оптимальные позиции
    spread = mexc_rate - binance_rate
    
    if spread > 0:
        optimal_mexc = "SHORT"
        optimal_binance = "LONG"
    else:
        optimal_mexc = "LONG"
        optimal_binance = "SHORT"
    
    # Рассчитываем прибыль для текущих позиций
    if mexc_pos and binance_pos:
        current_profit, mexc_pnl, binance_pnl = calculate_profit(
            mexc_rate, binance_rate, mexc_pos, binance_pos
        )
    else:
        current_profit = 0
        mexc_pnl = 0
        binance_pnl = 0
    
    # Рассчитываем прибыль для оптимальных позиций
    optimal_profit, optimal_mexc_pnl, optimal_binance_pnl = calculate_profit(
        mexc_rate, binance_rate, optimal_mexc, optimal_binance
    )
    
    # Проверяем корректность позиций
    positions_correct = (mexc_pos == optimal_mexc and binance_pos == optimal_binance)
    
    # Проверяем размеры позиций
    size_balanced = abs(mexc_size - binance_size) / max(mexc_size, binance_size, 1) < 0.05 if mexc_size > 0 and binance_size > 0 else False
    
    return {
        'current_profit': current_profit,
        'current_mexc_pnl': mexc_pnl,
        'current_binance_pnl': binance_pnl,
        'optimal_profit': optimal_profit,
        'optimal_mexc': optimal_mexc,
        'optimal_binance': optimal_binance,
        'optimal_mexc_pnl': optimal_mexc_pnl,
        'optimal_binance_pnl': optimal_binance_pnl,
        'positions_correct': positions_correct,
        'size_balanced': size_balanced,
        'has_positions': mexc_pos is not None and binance_pos is not None
    }


def create_message_with_positions(mexc_rate, binance_rate, analysis, mexc_pos, binance_pos, mexc_size, binance_size):
    """Создание сообщения с анализом реальных позиций"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    next_funding, hours, minutes = get_next_funding_time()
    
    # Определяем статус
    if analysis['has_positions']:
        if analysis['positions_correct'] and abs(analysis['current_profit']) >= SPREAD_THRESHOLD:
            emoji = "🟢"
            status = "POSITIONS CORRECT & PROFITABLE"
        elif analysis['positions_correct']:
            emoji = "🟡"
            status = "POSITIONS CORRECT BUT LOW PROFIT"
        else:
            emoji = "🔴"
            status = "POSITIONS INCORRECT!"
    else:
        if abs(analysis['optimal_profit']) >= SPREAD_THRESHOLD:
            emoji = "🟢"
            status = "OPPORTUNITY AVAILABLE"
        else:
            emoji = "⚪"
            status = "NO POSITIONS"
    
    message = f"""
{emoji} <b>{status}</b> {emoji}

📊 <b>Funding Rate Monitor</b>
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: <code>{SYMBOL}</code>
⏰ Time: <code>{timestamp}</code>
⏳ Next Funding: <code>{hours}h {minutes}m</code>

💹 <b>Funding Rates:</b>
├ MEXC: <code>{format_percentage(mexc_rate)}</code>
└ Binance: <code>{format_percentage(binance_rate)}</code>
"""
    
    # Раздел с текущими позициями
    if analysis['has_positions']:
        message += f"\n📍 <b>Your Current Positions:</b>\n"
        message += f"├ MEXC: <b>{mexc_pos}</b> ({mexc_size:.2f} contracts)\n"
        message += f"└ Binance: <b>{binance_pos}</b> ({binance_size:.2f} contracts)\n"
        
        # Проверка размеров
        if not analysis['size_balanced']:
            message += f"\n⚠️ <b>WARNING:</b> Position sizes not balanced!\n"
        
        # Текущая прибыль
        message += f"\n💰 <b>Your Current Profit:</b>\n"
        sign_mexc = "+" if analysis['current_mexc_pnl'] > 0 else ""
        sign_binance = "+" if analysis['current_binance_pnl'] > 0 else ""
        sign_total = "+" if analysis['current_profit'] > 0 else ""
        
        message += f"├ MEXC {mexc_pos}: <code>{sign_mexc}{format_percentage(analysis['current_mexc_pnl'])}</code>\n"
        message += f"├ Binance {binance_pos}: <code>{sign_binance}{format_percentage(analysis['current_binance_pnl'])}</code>\n"
        message += f"└ <b>Total: {sign_total}{format_percentage(abs(analysis['current_profit']))}</b>\n"
        
        # Проверка корректности
        if not analysis['positions_correct']:
            message += f"\n🚨 <b>ATTENTION: Wrong positions!</b>\n"
            message += f"You should have:\n"
            message += f"├ MEXC: <b>{analysis['optimal_mexc']}</b>\n"
            message += f"└ Binance: <b>{analysis['optimal_binance']}</b>\n"
            message += f"\n💸 <b>You're losing:</b> {format_percentage(abs(analysis['optimal_profit'] - analysis['current_profit']))}\n"
    else:
        message += f"\n📍 <b>No positions detected</b>\n"
    
    # Оптимальная стратегия
    message += f"\n📈 <b>Optimal Strategy:</b>\n"
    message += f"├ MEXC: <b>{analysis['optimal_mexc']}</b>\n"
    message += f"└ Binance: <b>{analysis['optimal_binance']}</b>\n"
    
    message += f"\n💰 <b>Optimal Profit:</b>\n"
    sign_opt_mexc = "+" if analysis['optimal_mexc_pnl'] > 0 else ""
    sign_opt_binance = "+" if analysis['optimal_binance_pnl'] > 0 else ""
    sign_opt_total = "+" if analysis['optimal_profit'] > 0 else ""
    
    message += f"├ MEXC {analysis['optimal_mexc']}: <code>{sign_opt_mexc}{format_percentage(analysis['optimal_mexc_pnl'])}</code>\n"
    message += f"├ Binance {analysis['optimal_binance']}: <code>{sign_opt_binance}{format_percentage(analysis['optimal_binance_pnl'])}</code>\n"
    message += f"└ <b>Total: {sign_opt_total}{format_percentage(abs(analysis['optimal_profit']))}</b>\n"
    
    message += f"\n🎯 <b>Threshold:</b> {format_percentage(SPREAD_THRESHOLD)}\n"
    
    # Прогноз прибыли
    if analysis['has_positions'] and analysis['positions_correct']:
        profit_rate = abs(analysis['current_profit'])
        avg_position_size = (mexc_size + binance_size) / 2
        
        # Прибыль до следующего funding
        profit_next = avg_position_size * profit_rate
        
        # Прибыль в день (3 раза)
        profit_daily = profit_next * 3
        
        # Прибыль в неделю
        profit_weekly = profit_daily * 7
        
        # Прибыль в месяц
        profit_monthly = profit_daily * 30
        
        message += f"\n💵 <b>Profit Forecast (Position: ${avg_position_size:.2f}):</b>\n"
        message += f"├ Next funding ({hours}h {minutes}m): <code>${profit_next:.2f}</code>\n"
        message += f"├ Daily (3x): <code>${profit_daily:.2f}</code>\n"
        message += f"├ Weekly: <code>${profit_weekly:.2f}</code>\n"
        message += f"└ Monthly: <code>${profit_monthly:.2f}</code>\n"
        
        # ROI
        roi_daily = (profit_daily / avg_position_size) * 100 if avg_position_size > 0 else 0
        roi_monthly = (profit_monthly / avg_position_size) * 100 if avg_position_size > 0 else 0
        message += f"\n📊 <b>ROI:</b> {roi_daily:.2f}% daily | {roi_monthly:.2f}% monthly\n"
    
    # Итоговое сообщение
    if analysis['has_positions']:
        if analysis['positions_correct'] and abs(analysis['current_profit']) >= SPREAD_THRESHOLD:
            message += f"\n✅ <b>Everything is correct! Keep positions open!</b>"
        elif analysis['positions_correct']:
            message += f"\n⚠️ <b>Positions correct but profit below threshold</b>"
        else:
            message += f"\n❌ <b>CLOSE and REVERSE positions immediately!</b>"
    else:
        if abs(analysis['optimal_profit']) >= SPREAD_THRESHOLD:
            message += f"\n✅ <b>Good opportunity! Open positions!</b>"
        else:
            message += f"\n⏳ <b>Wait for better opportunity...</b>"
    
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

        # Получаем текущие позиции
        print("Проверяем открытые позиции...")
        mexc_pos, mexc_size = get_positions(mexc, SYMBOL)
        binance_pos, binance_size = get_positions(binance, SYMBOL)
        
        # Анализируем позиции
        analysis = analyze_positions(
            mexc_rate, binance_rate,
            mexc_pos, binance_pos,
            mexc_size, binance_size
        )
        
        # Вывод в консоль
        print(f"\n" + "="*60)
        print(f"Funding Rates:")
        print(f"  MEXC:    {format_percentage(mexc_rate)}")
        print(f"  Binance: {format_percentage(binance_rate)}")
        print(f"  Spread:  {format_percentage(spread)}")
        
        if analysis['has_positions']:
            print(f"\n📍 Your Current Positions:")
            print(f"  MEXC:    {mexc_pos} ({mexc_size:.2f} contracts)")
            print(f"  Binance: {binance_pos} ({binance_size:.2f} contracts)")
            print(f"\n💰 Your Current Profit:")
            print(f"  MEXC {mexc_pos}:    {'+' if analysis['current_mexc_pnl'] > 0 else ''}{format_percentage(analysis['current_mexc_pnl'])}")
            print(f"  Binance {binance_pos}: {'+' if analysis['current_binance_pnl'] > 0 else ''}{format_percentage(analysis['current_binance_pnl'])}")
            print(f"  Total Profit: {'+' if analysis['current_profit'] > 0 else ''}{format_percentage(abs(analysis['current_profit']))}")
            
            if analysis['positions_correct']:
                print(f"\n✅ Positions are CORRECT!")
            else:
                print(f"\n❌ Positions are WRONG!")
                print(f"   Should be: MEXC {analysis['optimal_mexc']} / Binance {analysis['optimal_binance']}")
        else:
            print(f"\n📍 No positions detected")
        
        print(f"\n📈 Optimal Strategy:")
        print(f"  MEXC:    {analysis['optimal_mexc']}")
        print(f"  Binance: {analysis['optimal_binance']}")
        print(f"  Optimal Profit: {'+' if analysis['optimal_profit'] > 0 else ''}{format_percentage(abs(analysis['optimal_profit']))}")
        
        next_funding, hours, minutes = get_next_funding_time()
        print(f"\n⏳ Next funding in: {hours}h {minutes}m")
        print("="*60)

        # Создание и отправка сообщения
        message = create_message_with_positions(
            mexc_rate, binance_rate, analysis,
            mexc_pos, binance_pos, mexc_size, binance_size
        )
        await send_telegram_message(message)

    except Exception as e:
        error_message = f"❌ <b>ERROR</b>\n\n<code>{str(e)}</code>"
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        try:
            await send_telegram_message(error_message)
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
