"""Example Turing machines."""

from tm.machine import TuringMachine, Transition


def ends_with_zero() -> TuringMachine:
    """
    Accepts binary strings that contain at least one '1' followed eventually
    by a '0' (i.e. not all 1s and not ending in 1 before seeing a 0 after a 1).

    More precisely: scan right over 1s; on the first 0, accept.
    Reject if we only see 1s or halt without a valid transition.
    """
    transitions = {
        ("q0", "1"): Transition("q1", "1", "R"),
        ("q1", "0"): Transition("q_accept", "0", "R"),
    }
    return TuringMachine(
        states={"q0", "q1", "q_accept", "q_reject"},
        input_alphabet={"0", "1"},
        tape_alphabet={"0", "1", "_"},
        transitions=transitions,
        start_state="q0",
        accept_state="q_accept",
        reject_state="q_reject",
        name="ends-with-zero",
    )


def palindrome() -> TuringMachine:
    """
    Accepts binary palindromes over {0, 1}.

    Marks the leftmost unmarked symbol, scans to the rightmost unmarked
    symbol, and checks that they match. Rejects on mismatch; accepts when
    all symbols are matched (even length) or one marked symbol remains
    in the middle (odd length).
    """
    transitions = {
        # q0: find leftmost unmarked symbol and remember it via state
        ("q0", "0"): Transition("q_right_0", "X", "R"),
        ("q0", "1"): Transition("q_right_1", "X", "R"),
        ("q0", "X"): Transition("q0", "X", "R"),
        ("q0", "_"): Transition("q_accept", "_", "L"),
        # scan right looking for end of string
        ("q_right_0", "0"): Transition("q_right_0", "0", "R"),
        ("q_right_0", "1"): Transition("q_right_0", "1", "R"),
        ("q_right_0", "X"): Transition("q_right_0", "X", "R"),
        ("q_right_0", "_"): Transition("q_check_0", "_", "L"),
        ("q_right_1", "0"): Transition("q_right_1", "0", "R"),
        ("q_right_1", "1"): Transition("q_right_1", "1", "R"),
        ("q_right_1", "X"): Transition("q_right_1", "X", "R"),
        ("q_right_1", "_"): Transition("q_check_1", "_", "L"),
        # compare rightmost unmarked with remembered symbol
        ("q_check_0", "0"): Transition("q_left", "X", "L"),
        ("q_check_0", "1"): Transition("q_reject", "1", "L"),
        ("q_check_0", "X"): Transition("q_accept", "X", "L"),
        ("q_check_1", "1"): Transition("q_left", "X", "L"),
        ("q_check_1", "0"): Transition("q_reject", "0", "L"),
        ("q_check_1", "X"): Transition("q_accept", "X", "L"),
        # return to the left end
        ("q_left", "0"): Transition("q_left", "0", "L"),
        ("q_left", "1"): Transition("q_left", "1", "L"),
        ("q_left", "X"): Transition("q0", "X", "R"),
    }
    return TuringMachine(
        states={
            "q0",
            "q_right_0",
            "q_right_1",
            "q_check_0",
            "q_check_1",
            "q_left",
            "q_accept",
            "q_reject",
        },
        input_alphabet={"0", "1"},
        tape_alphabet={"0", "1", "X", "_"},
        transitions=transitions,
        start_state="q0",
        accept_state="q_accept",
        reject_state="q_reject",
        name="palindrome",
    )


MACHINES: dict[str, TuringMachine] = {
    "ends-with-zero": ends_with_zero(),
    "palindrome": palindrome(),
}


def get_machine(name: str) -> TuringMachine:
    if name not in MACHINES:
        available = ", ".join(sorted(MACHINES))
        raise KeyError(f"Unknown machine '{name}'. Available: {available}")
    return MACHINES[name]
