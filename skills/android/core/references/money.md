# Money

Referenced by `core DATA-2`.

## The representation

A monetary amount is **an integer of minor units plus its currency code**. Never a floating point
type.

    data class Money(val minorUnits: Long, val currencyCode: String)

`Long`, not `Int`, a mid-sized amount in a currency with a small unit exhausts a 32-bit integer
faster than people expect, and overflow in a total is worse than any rounding error.

## Why not a floating point type

Binary floating point cannot represent most decimal fractions exactly. `0.1 + 0.2` is not `0.3`.
Individually the error is invisible; summed over a long list it is not, and the total on the screen
does not match the total the server computed.

A decimal type (`BigDecimal`) avoids the representation problem but not the discipline problem, it
still lets you divide by 100, still lets an unrounded intermediate reach the UI, and costs
allocation on a scroll path. Integers of minor units make the wrong thing hard to write.

## The exponent belongs to the currency, not to 100

This is the half that ships broken.

| Currency | Minor units | 1000 minor units is |
|---|---:|---|
| USD, EUR, GBP | 2 | 10.00 |
| JPY, KRW | **0** | **1,000** |
| BHD, KWD, TND | **3** | **1.000** |

Dividing by a constant 100 renders a ¥1,000 order as ¥10. It is correct in every market the team
tests in, and wrong in the ones they do not.

Take the exponent from the platform's currency data rather than a constant:

    val currency = Currency.getInstance(money.currencyCode)
    val digits = currency.defaultFractionDigits      // 2, 0, or 3, and -1 for non-currencies

**Guard the negative.** `defaultFractionDigits` returns `-1` for codes that are not real currencies
(`XXX`, and metals like `XAU`). Treat that as "do not attempt to format as an amount" rather than
letting it become a shift by -1.

## Apply the exponent to the formatter, not only to the number

Getting the arithmetic right and leaving the formatter on its default gives you `¥1,000.00`, the
right amount with two decimal places a yen amount should not have.

    val fmt = NumberFormat.getCurrencyInstance()
    fmt.currency = currency
    fmt.minimumFractionDigits = digits
    fmt.maximumFractionDigits = digits

`NumberFormat.setCurrency` does **not** update the fraction digits on its own. Set them explicitly.

## Arithmetic

- Add and subtract minor units directly. Never mix currencies without an explicit conversion step
  that records the rate and when it was taken.
- Multiply before dividing, and decide the rounding rule deliberately, tax, discounts and splits
  each want a different one, and "whatever the language does by default" is a decision made by
  accident.
- A split that does not divide evenly must allocate the remainder to somebody. Dropping it means
  the parts do not sum to the whole.

## Formatting is a display concern

Format at the point of display, never at fetch or storage time (`core STATE-2`). A string built
when the data arrived carries the locale and currency settings that were current then, and nothing
downstream can sort, total, or re-render it.
