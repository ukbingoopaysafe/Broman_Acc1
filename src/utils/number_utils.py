def convert_arabic_to_english_digits(value):
    """
    Converts Arabic-Indic and Eastern Arabic-Indic digits in a string to English digits.
    Leaves other characters unchanged.
    """
    if not isinstance(value, str):
        value = str(value)
    translation_table = str.maketrans(
        "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
        "01234567890123456789"
    )
    return value.translate(translation_table)
