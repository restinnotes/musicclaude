"""Choose only a verified slider label under the account's explicit policy."""

def choose_effort(available, allow_high_fallback=False):
    if "Extra High" in available:
        return "Extra High", available["Extra High"], None
    if allow_high_fallback and "High" in available:
        return "High", available["High"], "extra_high_unavailable_high_authorized"
    raise ValueError("Extra High is unavailable and no authorized High selection exists")
