from dash import html

def format_number(num):
    """Format a numeric value with limited decimal places and thousands separators."""
    try:
        num = float(num)
    except:
        return str(num)

    num = round(num, 2)

    if num.is_integer():
        num = int(num)

    if abs(num) >= 10000:
        return f"{num:,}".replace(",", "_")

    return str(num)

def colorize_number(value, min_value, is_percentage=False):
    """Format a value and color it based on a specified threshold."""
    num = float(value)
    color = "#4CAF50" if num >= min_value else "#FF5722"

    if is_percentage:
        text = f"{num:.2%}"
    else:
        text = format_number(num)

    return html.Span(text, style={"color": color})