from tm.machine import TuringMachine, Transition


transitions = {

    ("q0", "1"): Transition(
        next_state="q1",
        write_symbol="1",
        move_direction="R"
    ),

    ("q1", "0"): Transition(
        next_state="q_accept",
        write_symbol="0",
        move_direction="R"
    )
}


simple_machine = TuringMachine(

    states={
        "q0",
        "q1",
        "q_accept",
        "q_reject"
    },

    input_alphabet={
        "0",
        "1"
    },

    tape_alphabet={
        "0",
        "1",
        "_"
    },

    transitions=transitions,

    start_state="q0",

    accept_state="q_accept",

    reject_state="q_reject"
)