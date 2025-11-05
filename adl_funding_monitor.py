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
SPREAD_THRESHOLD = 0.0001  # 0.01%
SYMBOL = 'APR/USDT:USDT'


def init_exchanges():
    """Инициализация бирж"""
    mexc = ccxt.mexc({
        'apiKey': MEXC_API_KEY,
        'secret': MEXC_API_SECRET,
        'timeout': 30000,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',
            'adjustForTimeDifference': True
        }
    })

    binance = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'timeout': 30000,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'adjustForTimeDifference': True
        }
    })

    return mexc, binance


def format_percentage(value):
    """Форматирование в проценты"""
    return f"{value * 100:.4f}%"


def get_adl_emoji(adl_value):
    """Получить эмодзи для ADL ranking"""
    if adl_value is None:
        return "⚪"

    adl = int(adl_value)
    if adl == 1:
        return "🟢"
    elif adl == 2:
        return "🟢🟢"
    elif adl == 3:
        return "🟡🟡🟡"
    elif adl == 4:
        return "🟠🟠🟠🟠"
    elif adl == 5:
        return "🔴🔴🔴🔴🔴"
    else:
        return "⚪"


def get_adl_risk_text(adl_value):
    """Получить текст риска ADL"""
    if adl_value is None:
        return "Unknown"

    adl = int(adl_value)
    if adl == 1:
        return "Very Low"
    elif adl == 2:
        return "Low"
    elif adl == 3:
        return "Medium"
    elif adl == 4:
        return "High"
    elif adl == 5:
        return "Very High"
    else:
        return "Unknown"


def get_positions_info(exchange, symbol):
    """Получить информацию о позициях включая ADL"""
    try:
        positions = exchange.fetch_positions([symbol])

        for pos in positions:
            contracts = float(pos.get('contracts', 0))
            print(f"contracts: {pos}")

            if contracts > 0:
                adl_value = None

                # Binance предоставляет adlQuantile
                if 'info' in pos and 'adlQuantile' in pos['info']:
                    adl_value = pos['info']['adlQuantile']

                # Безопасное получение leverage
                leverage = pos.get('leverage')
                if leverage is None or leverage == 0:
                    leverage = 'N/A'
                else:
                    leverage = f"{leverage}"

                # Безопасное получение PnL
                pnl = pos.get('unrealizedPnl', 0)
                if pnl is None:
                    pnl = 0

                return {
                    'has_position': True,
                    'side': pos.get('side', 'unknown'),
                    'size': contracts,
                    'leverage': leverage,
                    'unrealized_pnl': float(pnl),
                    'adl': adl_value
                }

        return {'has_position': False}

    except Exception as e:
        print(f"Ошибка получения позиций: {e}")
        return {'has_position': False, 'error': str(e)}


def create_message(mexc_rate, binance_rate, spread, mexc_pos_info, binance_pos_info):
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
    if spread > 0:
        direction = "SHORT MEXC / LONG Binance"
    else:
        direction = "LONG MEXC / SHORT Binance"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формируем сообщение
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
        message += f"\n✅ <b>Spread выше порога! Можно торговать!</b>\n"
    else:
        message += f"\n❌ Spread ниже порога. Ожидаем...\n"

    # Добавляем информацию о позициях
    message += "\n━━━━━━━━━━━━━━━━━━━━\n"
    message += "📍 <b>Current Positions:</b>\n\n"

    # MEXC позиция
    message += "🔷 <b>MEXC:</b>\n"
    if mexc_pos_info.get('has_position'):
        message += f"├ Side: <code>{mexc_pos_info['side'].upper()}</code>\n"
        message += f"├ Size: <code>{mexc_pos_info['size']}</code>\n"
        message += f"├ Leverage: <code>{mexc_pos_info['leverage']}x</code>\n"
        message += f"└ PnL: <code>${mexc_pos_info['unrealized_pnl']:.2f}</code>\n"
    else:
        message += "└ No position\n"

    message += "\n"

    # Binance позиция с ADL
    message += "🔶 <b>Binance:</b>\n"
    if binance_pos_info.get('has_position'):
        message += f"├ Side: <code>{binance_pos_info['side'].upper()}</code>\n"
        message += f"├ Size: <code>{binance_pos_info['size']}</code>\n"
        message += f"├ Leverage: <code>{binance_pos_info['leverage']}x</code>\n"
        message += f"├ PnL: <code>${binance_pos_info['unrealized_pnl']:.2f}</code>\n"

        # ADL информация
        adl = binance_pos_info.get('adl')
        if adl is not None:
            adl_emoji = get_adl_emoji(adl)
            adl_text = get_adl_risk_text(adl)
            message += f"└ ADL Risk: {adl_emoji} <b>{adl_text}</b> ({adl}/5)\n"
        else:
            message += "└ ADL: Not available\n"
    else:
        message += "└ No position\n"

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

        print("Получаем funding rates...")

        mexc_rate = None
        binance_rate = None
        errors = []

        # Получаем MEXC funding rate
        try:
            funding_mexc = mexc.fetch_funding_rate(SYMBOL)
            mexc_rate = funding_mexc['fundingRate']
            print(f"✓ MEXC rate получен: {mexc_rate}")
        except Exception as e:
            errors.append(f"MEXC: {str(e)}")
            print(f"✗ Ошибка MEXC: {e}")

        # Получаем Binance funding rate
        try:
            funding_binance = binance.fetch_funding_rate(SYMBOL)
            binance_rate = funding_binance['fundingRate']
            print(f"✓ Binance rate получен: {binance_rate}")
        except Exception as e:
            errors.append(f"Binance: {str(e)}")
            print(f"✗ Ошибка Binance: {e}")

        # Если данные не получены
        if mexc_rate is None or binance_rate is None:
            error_msg = "❌ <b>Ошибка получения данных</b>\n\n"
            error_msg += "\n".join([f"• {err}" for err in errors])
            await send_telegram_message(error_msg)
            return

        spread = mexc_rate - binance_rate

        print(f"\nfundingRate mexc: {mexc_rate}")
        print(f"fundingRate binance: {binance_rate}")
        print(f"fundingRate spread: {spread}")
        print(f"Spread %: {format_percentage(abs(spread))}")

        # Получаем информацию о позициях
        print("\nПолучаем информацию о позициях...")
        mexc_pos_info = get_positions_info(mexc, SYMBOL)
        binance_pos_info = get_positions_info(binance, SYMBOL)

        # Создание и отправка сообщения
        message = create_message(mexc_rate, binance_rate, spread, mexc_pos_info, binance_pos_info)
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