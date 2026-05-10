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

    return (
        f"Step {configuration.step}\n"
        f"State: {configuration.state}\n"
        f"{tape_string}\n"
        f"{head_string}\n"
    )