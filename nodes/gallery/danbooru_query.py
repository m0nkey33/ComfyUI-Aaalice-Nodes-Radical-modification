"""Danbooru search-tag budgeting."""

from __future__ import annotations

from .._lib.booru_query import normalize_tag_query, tokenize_tag_query


def danbooru_query_tag_count(query: str) -> int:
    return len(tokenize_tag_query(query))


def build_danbooru_search_tags(
    query: str,
    ratings: list[str],
    sort: str,
    size: int,
    public_tag_limit: int | None,
) -> str:
    tags = normalize_tag_query(query)
    query_tag_count = danbooru_query_tag_count(tags)
    if public_tag_limit is not None and query_tag_count > public_tag_limit:
        raise ValueError(f"danbooru supports at most {public_tag_limit} public search tags")

    if ratings:
        tags = f"{tags} rating:{','.join(ratings)}".strip()
    if sort == "random":
        if public_tag_limit is not None and query_tag_count >= public_tag_limit:
            raise ValueError(f"danbooru random sampling leaves room for only {public_tag_limit - 1} public search tag")
        tags = f"{tags} random:{size}".strip()
    elif sort and sort != "latest":
        # The order: metatag consumes one token of Danbooru's per-user search-tag
        # budget (unlike rating:, which is free). Drop it when the base query
        # already fills the budget, otherwise the API rejects the request with
        # HTTP 422 TagLimitError.
        if public_tag_limit is None or query_tag_count < public_tag_limit:
            tags = f"{tags} order:{sort}".strip()
    return tags


__all__ = ["build_danbooru_search_tags", "danbooru_query_tag_count"]
