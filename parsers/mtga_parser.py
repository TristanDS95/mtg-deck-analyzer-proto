def parse_mtga(text):


    card_pool = []
    for line in text.strip().splitlines():
        try:
            count, name = line.strip().split(" ", 1)
            card_pool.append({"name": name.strip(), "count": int(count)})
        except ValueError:
            continue
    return card_pool
