from reduction.tableau import ComputationTableau


class TableauEncoder:
    def __init__(self, tableau: ComputationTableau):
        self.tableau = tableau

    def generate_variables(self) -> list[str]:
        variables = []
        rows = self.tableau.generate_rows()
        
        for row_index, row in enumerate(rows):
            symbols = row.split()
            
            for column_index, symbol in enumerate(symbols):
                variable = (
                    f"CELL_"
                    f"{row_index}_"
                    f"{column_index}_"
                    f"{symbol}"
                )
                
                variables.append(variable)

        return variables