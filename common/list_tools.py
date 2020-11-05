def zipMerge(*lists):
    dicts = map(dict, lists)
    base = { }
    items = 0
    for d in dicts:
        items += 1
        for k,v in d.items():
            if k not in base:
                base[k] = [k] + [None] * len(lists)
            base[k][items] = v

    return map(list, sorted(base.values()))