from dataclasses import dataclass


@dataclass
class Variable:
    name: str
    
@dataclass
class Clause:
    literals: list[str]
    
class CNFFormula: 
    def __init__(self):
        self.clauses: list[Clause] = []
        
    def add_clause(self, clause: Clause) -> None:
        self.caluses.append(clause)
    
    def clause_count(self) -> int:
        return len(self.clauses)
    
    def variable_count(self) -> int:
        variables = set()
        for clause in self.clauses:
            for literal in clause.literals:
                variable = literal.replace("¬", "")
                variables.add(variable)
        return len(variables)