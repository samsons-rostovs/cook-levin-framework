from tm.configuration import Configuration


class ComputationTableau:
    
    def __init__(self, configurations: list[Configuration]):
        self.configurations = configurations
    
    def generate_rows(self) -> list[str]:
        rows = []
        
        for configuration in self.configurations:
            tape = configuration.tape.copy()
            tape.insert(
                configuration.head_position,
                f"[{configuration.state}]"
            )
            row = " ".join(tape)
            rows.append(row)
            
        return rows