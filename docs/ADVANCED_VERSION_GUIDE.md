# Руководство по расширенной версии (Advanced)

## Что нового?

### ✨ Основные возможности

1. **Проверка реальных позиций** - скрипт получает ваши открытые позиции с обеих бирж
2. **Анализ корректности** - проверяет, правильно ли открыты позиции
3. **Проверка балансировки** - сравнивает размеры позиций на обеих биржах
4. **🚨 КРИТИЧЕСКАЯ ПРОВЕРКА** - яркие предупреждения если позиция только на одной бирже
5. **ADL Risk Monitor** - показывает риск принудительной ликвидации (Auto-Deleveraging)
6. **Unrealized P&L** - отображает текущую нереализованную прибыль/убыток
7. **Прогноз прибыли** - рассчитывает прибыль до следующего funding и на перспективу
8. **Время до funding** - показывает, сколько осталось до следующей выплаты
9. **Детальные рекомендации** - что делать с текущими позициями

## Как это работает?

### 1. Получение позиций

Скрипт подключается к API бирж и получает:
- **Направление позиции** (LONG/SHORT)
- **Размер позиции** (количество контрактов)
- **Символ** (APR/USDT:USDT)

```python
# Пример вывода
MEXC:    SHORT (1000.00 contracts)
Binance: LONG  (1000.00 contracts)
```

### 2. Анализ корректности

Скрипт сравнивает ваши позиции с оптимальными:

**Если позиции правильные:**
```
✅ Positions are CORRECT!
Current Profit: +0.0600%
```

**Если позиции неправильные:**
```
❌ Positions are WRONG!
Should be: MEXC SHORT / Binance LONG
You're losing: 0.1200%
```

### 3. Проверка балансировки

Позиции должны быть примерно одинакового размера:

**Сбалансированные:**
```
MEXC:    SHORT (1000.00 contracts)
Binance: LONG  (1000.00 contracts)
✅ Balanced
```

**Несбалансированные:**
```
MEXC:    SHORT (1000.00 contracts)
Binance: LONG  (500.00 contracts)
⚠️ WARNING: Position sizes not balanced!
```

### 4. 🚨 Критическая проверка несбалансированных бирж

**НОВОЕ!** Если позиция открыта только на одной бирже, скрипт выдаст яркое предупреждение:

```
🚨🚨🚨 ВНИМАНИЕ @sappanara! 🚨🚨🚨

❌❌❌ КРИТИЧЕСКАЯ ОШИБКА! ❌❌❌

ПОЗИЦИЯ ОТКРЫТА ТОЛЬКО НА ОДНОЙ БИРЖЕ!
ОТСУТСТВУЕТ ПОЗИЦИЯ НА: BINANCE

ВЫ НЕСЕТЕ РЫНОЧНЫЙ РИСК БЕЗ ХЕДЖИРОВАНИЯ!
```

Предупреждение показывается:
- ✅ В начале сообщения (Telegram и консоль)
- ✅ В конце сообщения
- ✅ С упоминанием вашего username
- ✅ Крупными буквами и эмодзи

### 5. ADL Risk Monitor (Auto-Deleveraging)

Показывает риск принудительной ликвидации позиции:

```
⚠️ ADL Risk (Auto-Deleveraging):
├ MEXC: 🟢 Very Low (Level: 1)
└ Binance: 🟡 Low (Level: 2)
```

**Уровни риска:**
- 🟢 Level 1-2: Very Low / Low - безопасно
- 🟠 Level 3: Medium - следите за позицией
- 🔴 Level 4-5: High / Very High - высокий риск принудительного закрытия!

### 6. Unrealized P&L

Показывает текущую нереализованную прибыль/убыток:

```
💸 Unrealized P&L:
├ MEXC: +$125.50
├ Binance: -$45.20
└ Total: +$80.30
```

### 7. Прогноз прибыли

Скрипт рассчитывает прибыль на основе ваших реальных позиций:

```
💵 Profit Forecast (Position: $10,000.00):
├ Next funding (3h 45m): $6.00
├ Daily (3x): $18.00
├ Weekly: $126.00
└ Monthly: $540.00

📊 ROI: 0.18% daily | 5.40% monthly
```

## Примеры вывода

### Пример 1: Правильные позиции

```
🟢 POSITIONS CORRECT & PROFITABLE 🟢

📊 Funding Rate Monitor
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: APR/USDT:USDT
⏰ Time: 2024-11-05 04:50:00
⏳ Next Funding: 3h 10m

💹 Funding Rates:
├ MEXC: +0.0800%
└ Binance: +0.0200%

📍 Your Current Positions:
├ MEXC: SHORT (1000.00 contracts)
└ Binance: LONG (1000.00 contracts)

💰 Your Current Profit:
├ MEXC SHORT: +0.0800%
├ Binance LONG: -0.0200%
└ Total: +0.0600%

📈 Optimal Strategy:
├ MEXC: SHORT
└ Binance: LONG

💰 Optimal Profit:
├ MEXC SHORT: +0.0800%
├ Binance LONG: -0.0200%
└ Total: +0.0600%

🎯 Threshold: 0.0500%

💵 Profit Forecast (Position: $10,000.00):
├ Next funding (3h 10m): $6.00
├ Daily (3x): $18.00
├ Weekly: $126.00
└ Monthly: $540.00

📊 ROI: 0.18% daily | 5.40% monthly

✅ Everything is correct! Keep positions open!
```

---

### Пример 2: Неправильные позиции

```
🔴 POSITIONS INCORRECT! 🔴

📊 Funding Rate Monitor
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: APR/USDT:USDT
⏰ Time: 2024-11-05 04:50:00
⏳ Next Funding: 3h 10m

💹 Funding Rates:
├ MEXC: +0.0800%
└ Binance: +0.0200%

📍 Your Current Positions:
├ MEXC: LONG (1000.00 contracts)
└ Binance: SHORT (1000.00 contracts)

💰 Your Current Profit:
├ MEXC LONG: -0.0800%
├ Binance SHORT: +0.0200%
└ Total: -0.0600%

🚨 ATTENTION: Wrong positions!
You should have:
├ MEXC: SHORT
└ Binance: LONG

💸 You're losing: 0.1200%

📈 Optimal Strategy:
├ MEXC: SHORT
└ Binance: LONG

💰 Optimal Profit:
├ MEXC SHORT: +0.0800%
├ Binance LONG: -0.0200%
└ Total: +0.0600%

🎯 Threshold: 0.0500%

❌ CLOSE and REVERSE positions immediately!
```

---

### Пример 3: Нет позиций, но есть возможность

```
🟢 OPPORTUNITY AVAILABLE 🟢

📊 Funding Rate Monitor
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: APR/USDT:USDT
⏰ Time: 2024-11-05 04:50:00
⏳ Next Funding: 3h 10m

💹 Funding Rates:
├ MEXC: +0.0800%
└ Binance: +0.0200%

📍 No positions detected

📈 Optimal Strategy:
├ MEXC: SHORT
└ Binance: LONG

💰 Optimal Profit:
├ MEXC SHORT: +0.0800%
├ Binance LONG: -0.0200%
└ Total: +0.0600%

🎯 Threshold: 0.0500%

✅ Good opportunity! Open positions!
```

---

### Пример 4: 🚨 КРИТИЧЕСКАЯ ОШИБКА - Позиция только на одной бирже

```
🚨🚨🚨 ВНИМАНИЕ @sappanara! 🚨🚨🚨

❌❌❌ КРИТИЧЕСКАЯ ОШИБКА! ❌❌❌

ПОЗИЦИЯ ОТКРЫТА ТОЛЬКО НА ОДНОЙ БИРЖЕ!
ОТСУТСТВУЕТ ПОЗИЦИЯ НА: BINANCE

ВЫ НЕСЕТЕ РЫНОЧНЫЙ РИСК БЕЗ ХЕДЖИРОВАНИЯ!

━━━━━━━━━━━━━━━━━━━━
🚨🔴🚨 ⚠️ CRITICAL: UNBALANCED EXCHANGES ⚠️ 🚨🔴🚨

📊 Funding Rate Monitor
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: APR/USDT:USDT
⏰ Time: 2024-11-05 05:00:00
⏳ Next Funding: 3h 0m

💹 Funding Rates:
├ MEXC: +0.0800%
└ Binance: +0.0200%

📍 Your Current Positions:
├ MEXC: SHORT (1000.00 contracts)
└ Binance: ❌ NO POSITION ❌

⚠️ ADL Risk (Auto-Deleveraging):
├ MEXC: 🟢 Very Low (Level: 1)
└ Binance: ❓ Unknown

💸 Unrealized P&L:
├ MEXC: +$125.50
├ Binance: $0.00
└ Total: +$125.50

📈 Optimal Strategy:
├ MEXC: SHORT
└ Binance: LONG

💰 Optimal Profit:
├ MEXC SHORT: +0.0800%
├ Binance LONG: -0.0200%
└ Total: +0.0600%

🎯 Threshold: 0.0500%

━━━━━━━━━━━━━━━━━━━━
🚨🚨🚨 КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ! 🚨🚨🚨

@sappanara СРОЧНО ПРОВЕРЬТЕ ПОЗИЦИИ!

❌ НА BINANCE НЕТ ПОЗИЦИИ! ❌

ОТКРОЙТЕ ПОЗИЦИЮ НА BINANCE НЕМЕДЛЕННО!
ИНАЧЕ ВЫ РИСКУЕТЕ ПОТЕРЯТЬ ДЕНЬГИ ИЗ-ЗА ДВИЖЕНИЯ ЦЕНЫ!

🚨🚨🚨 ДЕЙСТВУЙТЕ СЕЙЧАС! 🚨🚨🚨
━━━━━━━━━━━━━━━━━━━━
```

---

### Пример 5: Несбалансированные размеры позиций

```
🟡 POSITIONS CORRECT BUT LOW PROFIT 🟡

📊 Funding Rate Monitor
━━━━━━━━━━━━━━━━━━━━
🪙 Symbol: APR/USDT:USDT
⏰ Time: 2024-11-05 04:50:00
⏳ Next Funding: 3h 10m

💹 Funding Rates:
├ MEXC: +0.0300%
└ Binance: +0.0200%

📍 Your Current Positions:
├ MEXC: SHORT (1000.00 contracts)
└ Binance: LONG (500.00 contracts)

⚠️ WARNING: Position sizes not balanced!

💰 Your Current Profit:
├ MEXC SHORT: +0.0300%
├ Binance LONG: -0.0200%
└ Total: +0.0100%

📈 Optimal Strategy:
├ MEXC: SHORT
└ Binance: LONG

💰 Optimal Profit:
├ MEXC SHORT: +0.0300%
├ Binance LONG: -0.0200%
└ Total: +0.0100%

🎯 Threshold: 0.0500%

⚠️ Positions correct but profit below threshold
```

## Использование

### Запуск

```bash
python funding_monitor_advanced.py
```

### Настройки

```python
# В файле funding_monitor_advanced.py

# Telegram настройки
TELEGRAM_USERNAME = '@sappanara'  # Ваш username для упоминаний в критических случаях

# Проверять реальные позиции
CHECK_POSITIONS = True  # False - только рекомендации

# Порог прибыльности
SPREAD_THRESHOLD = 0.0005  # 0.05%

# Торговая пара
SYMBOL = 'APR/USDT:USDT'
```

## Требования к API ключам

### MEXC
- ✅ Чтение позиций (Read Positions)
- ❌ Торговля (Trade) - не требуется

### Binance
- ✅ Чтение позиций (Read Positions)
- ❌ Торговля (Trade) - не требуется

## Интерпретация результатов

### Статусы

| Эмодзи | Статус | Значение |
|--------|--------|----------|
| 🚨🔴🚨 | CRITICAL: UNBALANCED EXCHANGES | **КРИТИЧНО!** Позиция только на одной бирже! |
| 🟢 | POSITIONS CORRECT & PROFITABLE | Всё правильно, прибыль выше порога |
| 🟡 | POSITIONS CORRECT BUT LOW PROFIT | Позиции правильные, но прибыль низкая |
| 🔴 | POSITIONS INCORRECT! | Позиции открыты неправильно - УБЫТОК! |
| 🟢 | OPPORTUNITY AVAILABLE | Нет позиций, но есть возможность |
| ⚪ | NO POSITIONS | Нет позиций и нет возможности |

### Действия

**🚨🔴🚨 CRITICAL: UNBALANCED EXCHANGES:**
- 🚨 **НЕМЕДЛЕННО** откройте позицию на недостающей бирже!
- 💀 Вы несете полный рыночный риск без хеджирования!
- 📉 Движение цены может привести к большим убыткам!
- ⚡ **ДЕЙСТВУЙТЕ СЕЙЧАС!** Это критическая ситуация!

**🟢 POSITIONS CORRECT & PROFITABLE:**
- ✅ Ничего не делать
- ✅ Держать позиции открытыми
- ✅ Получать funding каждые 8 часов

**🟡 POSITIONS CORRECT BUT LOW PROFIT:**
- ⚠️ Позиции правильные, но прибыль низкая
- 💭 Можно закрыть, если комиссии съедят прибыль
- ⏳ Или подождать изменения funding rates

**🔴 POSITIONS INCORRECT!:**
- ❌ СРОЧНО закрыть позиции
- 🔄 Открыть противоположные позиции
- 💸 Сейчас вы теряете деньги!

**🟢 OPPORTUNITY AVAILABLE:**
- ✅ Открыть позиции согласно рекомендациям
- 💰 Хорошая возможность для заработка

**⚪ NO POSITIONS:**
- ⏳ Ждать лучшей возможности
- 📊 Продолжать мониторинг

## Расчет прибыли

### Формулы

```python
# Прибыль за один funding период (8 часов)
profit_per_funding = position_size * profit_rate

# Прибыль в день (3 funding периода)
profit_daily = profit_per_funding * 3

# Прибыль в неделю
profit_weekly = profit_daily * 7

# Прибыль в месяц
profit_monthly = profit_daily * 30

# ROI (Return on Investment)
roi_daily = (profit_daily / position_size) * 100
roi_monthly = (profit_monthly / position_size) * 100
```

### Пример

```
Position: $10,000
Profit Rate: 0.06% (0.0006)

Profit per funding: $10,000 × 0.0006 = $6
Profit daily: $6 × 3 = $18
Profit weekly: $18 × 7 = $126
Profit monthly: $18 × 30 = $540

ROI daily: ($18 / $10,000) × 100 = 0.18%
ROI monthly: ($540 / $10,000) × 100 = 5.40%
```

## Время funding

Funding выплачивается **каждые 8 часов** в:
- **00:00 UTC**
- **08:00 UTC**
- **16:00 UTC**

Скрипт автоматически рассчитывает время до следующего funding:

```
⏳ Next Funding: 3h 10m
```

## Troubleshooting

### Ошибка: "No positions detected"

**Причины:**
1. У вас действительно нет открытых позиций
2. API ключи не имеют прав на чтение позиций
3. Неправильный формат символа

**Решение:**
1. Проверьте позиции в веб-интерфейсе биржи
2. Убедитесь, что API ключи имеют права "Read Positions"
3. Проверьте, что `SYMBOL = 'APR/USDT:USDT'` правильный

### Ошибка: "Position sizes not balanced"

**Причина:** Размеры позиций на биржах отличаются более чем на 5%

**Решение:**
1. Откройте дополнительную позицию на бирже с меньшим размером
2. Или закройте часть позиции на бирже с большим размером

### Позиции показаны неправильно

**Причина:** Биржа возвращает позиции в нестандартном формате

**Решение:**
1. Проверьте вывод в консоли
2. Убедитесь, что используете фьючерсный аккаунт
3. Проверьте настройки `defaultType` в коде

## Сравнение версий

| Функция | Базовая версия | Расширенная версия |
|---------|----------------|-------------------|
| Получение funding rates | ✅ | ✅ |
| Рекомендации по позициям | ✅ | ✅ |
| Проверка реальных позиций | ❌ | ✅ |
| Анализ корректности | ❌ | ✅ |
| Проверка балансировки | ❌ | ✅ |
| 🚨 Критические предупреждения | ❌ | ✅ |
| ADL Risk Monitor | ❌ | ✅ |
| Unrealized P&L | ❌ | ✅ |
| Прогноз прибыли | Примерный | Точный |
| Время до funding | ❌ | ✅ |
| ROI расчет | ❌ | ✅ |
| Упоминание в Telegram | ❌ | ✅ |

## Рекомендации

1. **Запускайте скрипт регулярно** (каждые 5-10 минут)
2. **Следите за балансировкой** позиций
3. **Закрывайте позиции**, если они неправильные
4. **Учитывайте комиссии** при расчете прибыли
5. **Используйте стоп-лоссы** для управления рисками

## Автоматизация

### Cron (Linux/Mac)

```bash
# Каждые 5 минут
*/5 * * * * cd /path/to/project && python funding_monitor_advanced.py

# Каждые 10 минут
*/10 * * * * cd /path/to/project && python funding_monitor_advanced.py

# Перед каждым funding (за 5 минут)
55 */8 * * * cd /path/to/project && python funding_monitor_advanced.py
```

### Task Scheduler (Windows)

1. Откройте Task Scheduler
2. Создайте новую задачу
3. Триггер: Повторять каждые 5 минут
4. Действие: Запустить `python funding_monitor_advanced.py`

## Заключение

Расширенная версия скрипта дает вам **полный контроль** над вашими позициями:

- ✅ Видите реальное состояние позиций на обеих биржах
- ✅ Знаете, правильно ли они открыты
- 🚨 **КРИТИЧЕСКИЕ ПРЕДУПРЕЖДЕНИЯ** если позиция только на одной бирже
- ⚠️ Мониторинг ADL риска принудительной ликвидации
- 💸 Отслеживание нереализованной прибыли/убытка
- ✅ Получаете точный прогноз прибыли
- ✅ Знаете, когда будет следующая выплата
- ✅ Получаете четкие рекомендации с упоминанием в критических случаях

Теперь вы можете быть уверены, что ваши позиции приносят прибыль и **никогда не пропустите критическую ситуацию**! 🚀
