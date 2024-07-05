from code_analysis import *
from code_generation import *

# File
file = "testing/Test6.cp"

# Transition Table
table = get_table("parameters/TTFinal.txt")

# LL1 Table
ll_table = get_table("parameters/ll1.txt")

# Grammar
grammar = get_grammar("parameters/grammar.txt")

def compile(file_name, table, ll_table, grammar):
    # Check that file extension is correct (.cp)
    if file_name[-3:] != ".cp":
        return
    
    print("Lexical now")
    tokens = lexical_analysis(file_name, table)
    
    token_file = open("tokens_lexical.txt", "w")
    for token in tokens:
        token_file.write(f"{token[0]} {token[1]}\n")
    token_file.close()
    
    print("Syntax now")
    tokens = syntax_analysis(file_name, tokens, grammar, ll_table)
    if not tokens: # Syntax error
        print(tokens)
        print("Syntax error, program will not proceed")
        return 1
    print(tokens)
    token_file = open("tokens_syntax.txt", "w")
    for token in tokens:
        token_file.write(f"{token[0]} {token[1]}\n")
    token_file.close()
    
    print("Semantic now")
    if not semantic_analysis(file_name, tokens, grammar, ll_table):
        return 1
    
    print("Code generation now")
    if not generate_code(file_name, tokens, grammar, ll_table):
        return 1
    
    print("Literally nothing wrong") # Prints if no errors :D
    return 0

compile(file, table, ll_table, grammar)