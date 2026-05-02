# Reusable pagination utility helpers
import math


def paginate_query(query, page: int = 1, page_size: int = 10):
    page = max(page, 1)
    size = max(min(page_size, 100), 1)

    total_items = query.count()
    offset = (page - 1) * size

    items = query.offset(offset).limit(size).all()

    meta = build_meta(page, size, total_items)

    return items, meta


def build_meta(page: int, page_size: int, total_items: int):
    total_pages = math.ceil(total_items / page_size) if page_size else 1

    return {
        "page": page,
        "size": page_size,
        "total": total_items,
        "total_pages": total_pages
    }
