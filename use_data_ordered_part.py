from make_json_ordered_parts import ordered_part


def count_unique_paths():
    # Count unique paths
    def unique_paths(routes):
        seen = set()
        for path in routes:
            seen.add(tuple(path))
        return seen

    all_unique = unique_paths(ordered_part.route)

    print(f"{len(all_unique)} unique paths total")

    # Convert tuples back to lists for easier use
    return [list(p) for p in all_unique]
different_paths = count_unique_paths()
print(different_paths)

