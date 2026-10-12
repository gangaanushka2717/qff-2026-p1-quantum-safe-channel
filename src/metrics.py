
def summarize_metrics(results):
    """Return a simple summary of measured experiment results."""
    if not results:
        return {
            "num_runs": 0,
            "success_rate": None,
        }

    successful_runs = sum(
        1 for result in results if result.get("success") is True
    )

    return {
        "num_runs": len(results),
        "success_rate": successful_runs / len(results),
    }
