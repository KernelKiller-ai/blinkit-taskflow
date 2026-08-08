from app.core.algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    insertion_sort_count,
    binary_search_count,
    linear_search_count,
)


def run_check(case_name: str, actual, expected) -> None:
    """Prints PASS or FAIL line according to Section 2 specification."""
    if actual == expected:
        print(f"PASS: {case_name}")
    else:
        print(f"FAIL: {case_name} — expected {expected}, got {actual}")


if __name__ == "__main__":
    # Case 1: insertion_sort on empty list
    empty_list = []
    insertion_sort(empty_list, key="title")
    run_check("insertion_sort on empty list", empty_list, [])

    # Case 2: insertion_sort on single-element list
    single_item = [{"title": "Alpha"}]
    insertion_sort(single_item, key="title")
    run_check("insertion_sort on single-element list", single_item, [{"title": "Alpha"}])

    # Case 3: binary_search at first, middle, and last index
    sorted_records = [
        {"val": 10},
        {"val": 20},
        {"val": 30},
        {"val": 40},
        {"val": 50},
    ]
    first_idx = binary_search(sorted_records, 10, key="val")
    mid_idx = binary_search(sorted_records, 30, key="val")
    last_idx = binary_search(sorted_records, 50, key="val")
    run_check(
        "binary_search first, middle, and last index",
        (first_idx, mid_idx, last_idx),
        (0, 2, 4),
    )

    # Case 4: binary_search absent target
    absent_idx = binary_search(sorted_records, 99, key="val")
    run_check("binary_search target absent", absent_idx, -1)

    # Case 5: insertion_sort_count mutates correctly & returns plain int > 0
    sort_test_list = [{"val": 30}, {"val": 10}, {"val": 20}]
    comps = insertion_sort_count(sort_test_list, key="val")
    is_sorted = sort_test_list == [{"val": 10}, {"val": 20}, {"val": 30}]
    is_valid_count = type(comps) is int and comps > 0
    run_check(
        "insertion_sort_count mutation and count validation",
        (is_sorted, is_valid_count),
        (True, True),
    )

    # Case 6: binary_search_count returns dict with index and comparison_count > 0
    bs_count_res = binary_search_count(sorted_records, 30, key="val")
    is_bs_dict_valid = (
        isinstance(bs_count_res, dict)
        and bs_count_res.get("index") == 2
        and type(bs_count_res.get("comparison_count")) is int
        and bs_count_res.get("comparison_count") > 0
    )
    run_check("binary_search_count result format and values", is_bs_dict_valid, True)

    # Case 7: linear_search_count for absent value returns index -1 and count == len(list)
    ls_test_list = [{"val": 1}, {"val": 2}, {"val": 3}, {"val": 4}]
    ls_count_res = linear_search_count(ls_test_list, 99, key="val")
    expected_ls_res = {"index": -1, "comparison_count": len(ls_test_list)}
    run_check("linear_search_count absent value", ls_count_res, expected_ls_res)