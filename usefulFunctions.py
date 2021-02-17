
def split_text(plainText, start, end):
    if start != '':
        usefullText = plainText.split(start)[1]
    else:
        usefullText = plainText
    if end != '':
        usefullText = usefullText.split(end)[0]
    return usefullText.strip()
