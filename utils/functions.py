def format_number(num):
    return '{:,.0f}'.format(num).replace(',', ' ')


def format_number_col(col):
    return col.map(lambda x: format_number(x))



