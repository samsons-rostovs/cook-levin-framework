from tm.configuration import Configuration


def render_configuration(configuration: Configuration) -> str:

    tape_string = " ".join(configuration.tape)

    head_line = []

    for index in range(len(configuration.tape)):

        if index == configuration.head_position:
            head_line.append("^")
        else:
            head_line.append(" ")

    head_string = " ".join(head_line)

    output = (
        f"Step {configuration.step}\n"
        f"State: {configuration.state}\n"
        f"{tape_string}\n"
        f"{head_string}\n"
    )

    if configuration.execution_step is not None:
        output += (
            f"Read: {configuration.execution_step.read_symbol}\n"
            f"Write: {configuration.execution_step.write_symbol}\n"
            f"Move: {configuration.execution_step.move_direction}\n"
            f"Next state: {configuration.execution_step.next_state}\n"
        )
    return output