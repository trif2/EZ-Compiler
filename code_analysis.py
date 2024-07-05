# Constants
TERMINALS = "abcdefghijklmnopqrstuvwxyz0123456789()<>=,+-*/%;"

KEYWORDS = [
    "def",
    "fed",
    "int",
    "double",
    "if",
    "fi",
    "else",
    "then",
    "while",
    "do",
    "od",
    "print",
    "return",
    "or",
    "and",
    "not"
]

FINAL_STATES = [False,
    True, 
    True, 
    True, 
    False, 
    False, 
    True, 
    True, 
    False, 
    False, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True, 
    True,
    True,
    True,
    True, 
    False
]

DELIM_STATE = 27

BUF_SIZE = 2048

# Global Variables
bflag = True # Read from buf1 if true, read from buf2 if false
table = []

# Buffers initialized in lexicalAnalysis()
buf1 = []
buf2 = []
# Iterators for all methods
line_count = 1
col_count = 1

# Iterators for lexicalAnalysis()
prev_state = 0
curr_state = 0
is_eof = False

# Function for importing tables from .txt files
def get_table(file):
    with open(file, "r") as fp:
        first_line = fp.readline().strip()
        second_line = fp.readline().strip()
        rows = int(first_line)
        cols = int(second_line)
        # Initialize fixed sized 2D list
        table = [[0] * cols for i in range(rows)]
        line = fp.readline().strip()
        
        # Row ptr
        i = 0
        
        while line:
            temp = line.split("\t")
            for j in range(cols):
                table[i][j] = int(temp[j])
            i += 1 
            line = fp.readline().strip()
    return table

# Function for importing grammar from .txt files
def get_grammar(file):
    table = []
    with open(file, "r") as fp:
        line = fp.readline().strip()
        while line:
            table.append(line.split(" "))
            line = fp.readline().strip()
    return table

# Returns a buffer (list) of size 2048
def get_buffer(fp):
    global BUF_SIZE
    buf_str = fp.read(BUF_SIZE)
    # Initialize char array of size 2048
    buf_arr = [""] * BUF_SIZE
    for i in range(len(buf_str)):
        buf_arr[i] = buf_str[i]
    return buf_arr

# Returns the token based on the state and lexeme
def get_token_from_ID(state, lexeme):
    if state == 1: # Identifier, but check for keyword
        n = len(KEYWORDS)
        for i in range(n):
            if lexeme == KEYWORDS[i]: # if lexeme is a keyword
                return lexeme
        return "iden"
    elif state == 2: # iden
        return "iden"
    elif state == 3 or state == 6: # int
        return "RINT"
    elif state == 7 or state == 10: # double
        return "RDBL"
    elif state == 14: # =
        return "="
    elif state >= 11 and state <= 17: # relop
        return "RELOP"
    elif state == 18: # op
        return "OP1"
    elif state == 19: # (
        return "OP2"
    elif state == 20: # )
        return "("
    elif state == 21: # ;
        return ")"
    elif state == 22: # ;
        return "["
    elif state == 23: # ;
        return "]"
    elif state == 24: # ,
        return ","
    elif state == 25: # .
        return "."
    elif state == 26: # ;
        return ";"
    return "" # curr_state is delim state

# Iterates through the buffer and returns the next token
def getNextToken(fp, err_file, lexeme_begin, panic_mode, table):
    global bflag
    global buf1
    global buf2
    global is_eof
    global line_count
    global col_count
    global FINAL_STATES
    forward = lexeme_begin
    change_buf = False
    panic_mode = False
    
    curr_state = 0
    prev_state = 0
    
    # Added to prevent program failure
    curr_token = -1
    
    # Treat curr_lexeme as char pointer !!!
    curr_lexeme = []
    found_token = False
    while not found_token:
        print(curr_lexeme)
        # Check if forward index is in bounds
        if forward >= 2048:
            forward = 0
            bflag = not bflag
            change_buf = True
        
        # Read from buffer based off bflag
        if bflag:
            char = buf1[forward]
        else:
            char = buf2[forward]
        
        # EOF CHECK
        if char == "":
            is_eof = True
            if FINAL_STATES[curr_state] or curr_state == DELIM_STATE: # Return curr_state as curr_token
                curr_token = curr_state
                break
            else:
                generate_lexical_error(lexeme_begin, forward, curr_lexeme, line_count, col_count, char)
                curr_token = DELIM_STATE
                break
            
        char_value = ord(char)
        prev_state = curr_state
        curr_state = table[curr_state][char_value]
        
        if panic_mode:
            if char_value == 9 or char_value == 10 or char_value == 32: # If delimiter
                curr_state = 0
                prev_state = 0
                panic_mode = False
                curr_token = DELIM_STATE
            forward += 1
            
        elif curr_state == -1: # Error State
            generate_lexical_error(lexeme_begin, forward, curr_lexeme, line_count, col_count, char)
            forward += 1
            if FINAL_STATES[prev_state] == True:
                curr_token = prev_state
                break
            panic_mode = True
            break
            
        elif curr_state == 0 and prev_state != DELIM_STATE: #
            if FINAL_STATES[prev_state] == True:
                curr_token = prev_state
                break
            else: # I don't think this will ever be checked
                generate_lexical_error(lexeme_begin, forward, curr_lexeme, line_count, col_count, char)
        elif curr_state == 0 and prev_state == DELIM_STATE:
            curr_token = DELIM_STATE
        elif curr_state == DELIM_STATE: # if curr_state == delim
            forward += 1
        else:
            if (char != " " and char != "\t" and char != "\n"):
                curr_lexeme.append(char)
            forward += 1
        
        
        if char == "\n":
            line_count += 1
            col_count = 0
        else:
            col_count += 1

    # then change the buffer
    if change_buf:
        print("changed buffer")
        if bflag:
            buf2 = get_buffer(fp)
        else:
            buf1 = get_buffer(fp)
    
    # move lexeme_begin
    new_lexeme_begin = forward
    
    curr_lexeme = "".join(curr_lexeme)
    
    final_token = get_token_from_ID(curr_token, curr_lexeme)
    return final_token, curr_lexeme, new_lexeme_begin, panic_mode

# Main function for getting the tokens
def lexical_analysis(file, table):
    tokens = []
    fp = open(file, "r")
    err_file = open("err_files/lexical_error_log.txt", "w")
    
    lexeme_begin = 0
    
    global buf1
    global buf2
    global is_eof
    
    buf1 = get_buffer(fp)
    buf2 = get_buffer(fp)


    panic_mode = False
    
    while not is_eof:
        curr_token, curr_lexeme, lexeme_begin, panic_mode = getNextToken(fp, err_file, lexeme_begin, panic_mode, table)
        if curr_token:
            tokens.append([curr_token, curr_lexeme])
    fp.close()
    err_file.close()
    return tokens

# Function for generating lexical errors (obv)
def generate_lexical_error(lexeme_begin, forward, curr_lexeme, line_count, col_count, invalid_char):
    print("Lexical error at", forward)
    print("See err_files/lexical_error_log.txt for more details")
    err_file = open("err_files/lexical_error_log.txt", "w")
    
    global file
    lex_len = forward - lexeme_begin
    curr_lexeme_str = "".join(curr_lexeme)
    if lex_len <= 0:
        lex_len += 2048
    err_file.write(f"File \"{file}\", line {line_count}, col {col_count}.\n\tInvalid Token Error: \"{curr_lexeme_str}{invalid_char}\"\n")
    err_file.write("\t                      ")
    dot_count = lex_len
    if dot_count >= 2048:
        dot_count -= 2048
    for i in range(dot_count):
        err_file.write(".")
    err_file.write("^")
    err_file.write("...")
    err_file.write("\n\n")
    return

# PHASE 2

# Returns the token enum based on the token string (for syntax_analysis and semantic_analysis)
def token_enum(token): 
    if token[0] == ".":
        result = 0
    elif token[0] == ";":
        result = 1
    elif token[0] == "def":
        result = 2
    elif token[0] == "iden":
        result = 3
    elif token[0] == "(":
        result = 4
    elif token[0] == ")":
        result = 5
    elif token[0] == "fed":
        result = 6
    elif token[0] == ",":
        result = 7
    elif token[0] == "int":
        result = 8
    elif token[0] == "double":
        result = 9
    elif token[0] == "=":
        result = 10
    elif token[0] == "if":
        result = 11
    elif token[0] == "then":
        result = 12
    elif token[0] == "while":
        result = 13
    elif token[0] == "do":
        result = 14
    elif token[0] == "od":
        result = 15
    elif token[0] == "print":
        result = 16
    elif token[0] == "return":
        result = 17
    elif token[0] == "fi":
        result = 18
    elif token[0] == "else":
        result = 19
    elif token[0] == "OP1":
        result = 20
    elif token[0] == "OP2":
        result = 21
    elif token[0] == "[":
        result = 22
    elif token[0] == "]":
        result = 23
    elif token[0] == "or":
        result = 24
    elif token[0] == "and":
        result = 25
    elif token[0] == "not":
        result = 26
    elif token[0] == "RELOP":
        result = 27
    elif token[0] == "RINT":
        result = 28
    elif token[0] == "RDBL":
        result = 29
    elif token[0] == "$":
        result = 30
    return result

# Replaces the token string with the token enum (for syntax_analysis and semantic_analysis)
def create_token(token_str):
    if token_str == "RINT":
        return [token_str, "0"]
    elif token_str == "RDBL":
        return [token_str, "0.0"]
    elif token_str == "OP1":
        return [token_str, "+"]
    elif token_str == "OP2":
        return [token_str, "*"]
    return [token_str, token_str]    

# Main function for syntax analysis
def syntax_analysis(file, tokens, grammar, ll_table):
    stack = []
    stack.append("$")
    stack.append("0")
    i = 0
    err_count = 0
    while len(stack) > 0 and i < len(tokens):
        curr_token = tokens[i]
        print(stack)
        peek = stack[-1]
        if peek == tokens[i][0]:
            err_count = 0
            i += 1
            stack.pop()
            continue
        elif peek == "@":
            stack.pop()
            continue
        curr_token = tokens[i]
        if not peek.isdigit(): # Missing terminal, continues parsing until valid terminal is found. If missing, parser adds terminal to tokens
            if peek == "$":
                print("Could not resolve syntax error")
                return tokens
            if err_count == 0:
                generate_syntax_error(file, tokens, i, stack, curr_token[0])
            err_count += 1
            tokens.insert(i, create_token(peek))
            continue
            

        row = int(peek)
        col = token_enum(curr_token)
        print(f"({row}, {col})")
        prod_to_add = ll_table[row][col]
        if prod_to_add == -1: # Wrong non-terminal, pop until tokens[i] is in ll1 table
            if err_count == 0:
                generate_syntax_error(file, tokens, i, stack, curr_token[0])
            err_count += 1
            tokens.pop(i)
            continue
        curr_prod = grammar[prod_to_add]
        stack.pop()
        for j in range(len(curr_prod) - 1, -1, -1):
            stack.append(curr_prod[j])
    if len(stack) != 1:
        generate_syntax_error(file, tokens, i, stack, False)
        return []
    return tokens

# Function for generating syntax errors (obv)
def generate_syntax_error(file, tokens, i, char, stack, expected_token=False):
    print("Syntax Error at", i)
    print("See err_files/syntax_error_log.txt for more details")
    err_file = open("err_files/syntax_error_log.txt", "w")
    err_file.write(f"File \"{file}\".\n\tSyntax Error: ")
    
    if i > len(tokens) - 1:
        print("Could not resolve syntax error")
        return
    prev_tokens = tokens[max(0, i-4):i]
    next_tokens = tokens[i+1:min(i+5, len(tokens))]
    if expected_token:
        err_file.write(f"Expected token {stack[-1]} but didn't find it\n")
    else:
        for token in prev_tokens:
            err_file.write(token[1] + " ")
        err_file.write(f"  >>> {tokens[i][1]} <<<  ")
        for token in next_tokens:
            err_file.write(token[1] + " ")
        err_file.write("\n")

    return

# PHASE 3

# Checks if the identifier is in the local scope
def find_iden_local(symbol_table, iden):
    for i in range(len(symbol_table.table)):
        if symbol_table.table[i].iden == iden:
            return True
    return False

# Checks if the identifier is in the global scope
def find_iden_global(symbol_table, iden):
    curr_table = symbol_table
    
    while curr_table is not None:
        for i in range(len(curr_table.table)):
            if curr_table.table[i].iden == iden:
                return True
        curr_table = curr_table.parent
        
    return False

# Returns the type of the identifier (only called if identifier exists in a scope)
def get_iden_type(symbol_table, iden):
    curr_table = symbol_table
    
    while curr_table is not None:
        for i in range(len(curr_table.table)):
            if curr_table.table[i].iden == iden:
                return curr_table.table[i].type
        curr_table = curr_table.parent
        
    return None

# Returns the number of parameters of the function
def get_func_param_num(symbol_table, iden):
    curr_table = symbol_table
    
    while curr_table is not None:
        for i in range(len(curr_table.table)):
            if curr_table.table[i].iden == iden:
                return curr_table.table[i].num_params
        curr_table = curr_table.parent
    
    return None

# Returns the parameters of a function (from the symbol table)
def get_func_params(symbol_table, iden):
    curr_table = symbol_table
    
    while curr_table is not None:
        for i in range(len(curr_table.table)):
            if curr_table.table[i].iden == iden:
                return curr_table.table[i].params
        curr_table = curr_table.parent
    
    return None

"""
semantic_analysis(file, tokens)

This is a modified syntax_analysis()

There are 4 cases to consider for scope:
1. fdec, new scope + variable(s)
2. decl, new variable(s)
3. if statement, new scope
4. else statement, new scope
Note: 3 and 4 are different

There are 3 cases to consider for type checking:
1. bexpr, check type of all idens in bexpr (if (<bexpr>), while <bexpr>)
2. statement -> var = expr, check type of var, and all types of expr
3. statement -> return expr, check type of expr against func type

ALKFJSLDKJFLKAJFLKSJDKLFJSDKLJFALKFJLKSDJF (this took really long)
"""
def semantic_analysis(file, tokens, grammar, ll_table): 
    table_global = SymbolTable()
    curr_table = table_global
    
    is_fdec = False
    is_decl = False
    is_var_eq_expr = False
    is_if_or_while_statement = False
    is_else_statement = False
    is_print_statement = False
    is_return_statement = False
    
    stack = []
    stack.append("$")
    stack.append("0")
    i = 0
    
    end_temp_stack_len = 0
    return_type = None
    curr_var_type = None
    curr_func = None
    
    first_type = None
    to_print = False
    
    while len(stack) > 0 and i < len(tokens):
        curr_token = tokens[i]
        peek = stack[-1]
        if to_print and len(stack) == end_temp_stack_len:
            to_print = False
            first_type = None
        
        if return_type is not None and len(stack) == end_temp_stack_len:
            return_type = None
        
        if curr_var_type is not None and len(stack) == end_temp_stack_len:
            curr_var_type = None
        
        if peek == tokens[i][0]:
            if tokens[i][0] == "fed": # Delete local symbol table and set curr_func to None
                curr_table = curr_table.parent
                curr_table.sub_table = None
                curr_func = None
            if tokens[i][0] == "fi": # Delete local symbol table
                curr_table = curr_table.parent
                curr_table.sub_table = None
            elif tokens[i][0] == "iden": # Check if iden in scope
                if not find_iden_global(curr_table, tokens[i][1]):
                    generate_semantic_error(file, tokens, i, True)
                    return False
                if i + 1 < len(tokens) and tokens[i+1][0] == "(": # Check function parameters
                    # Check how many parameters the function CALL has
                    parentheses_count = 1
                    param_count = 1
                    if tokens[i+2][0] == ")":
                        param_count = 0
                        parentheses_count = 0
                    j = i + 2
                    while parentheses_count > 0:
                        if tokens[j][0] == "(":
                            parentheses_count += 1
                        elif tokens[j][0] == ")":
                            parentheses_count -= 1
                        elif tokens[j][0] == "," and parentheses_count == 1:
                            param_count += 1
                        j += 1
                    # Check if the function definition has the same number of parameters
                    if get_func_param_num(curr_table, tokens[i][1]) is None or get_func_param_num(curr_table, tokens[i][1]) != param_count:
                        generate_semantic_error(file, tokens, i, False, True)
                        return False
                    
                    # Iterate through parameters and check if they match param_type
                    k = i + 2
                    curr_param = 0
                    curr_param_type = get_func_params(curr_table, tokens[i][1])
                    while k < j:
                        if tokens[k][0] == "iden":
                            if not find_iden_global(curr_table, tokens[k][1]):
                                generate_semantic_error(file, tokens, k, True)
                                return False
                            elif get_iden_type(curr_table, tokens[k][1]) != curr_param_type[curr_param]:
                                generate_semantic_error(file, tokens, k, False, False, False, True)
                                return False
                        elif tokens[k][0] == "RINT":
                            if curr_param_type[curr_param] != "int":
                                generate_semantic_error(file, tokens, k, False, False, False, True)
                                return False
                        elif tokens[k][0] == "RDBL":
                            if curr_param_type[curr_param] != "double":
                                generate_semantic_error(file, tokens, k, False, False, False, True)
                                return False
                        elif tokens[k][0] == ",":
                            curr_param += 1
                        k += 1
                if to_print:
                    if first_type is None:
                        first_type = get_iden_type(curr_table, tokens[i][1])
                    else:
                        if get_iden_type(curr_table, tokens[i][1]) != first_type:
                            generate_semantic_error(file, tokens, i)
                            return False
                if curr_var_type is not None:
                    if get_iden_type(curr_table, tokens[i][1]) != curr_var_type:
                        generate_semantic_error(file, tokens, i)
                        return False
                if return_type is not None:
                    if get_iden_type(curr_table, tokens[i][1]) != return_type:
                        generate_semantic_error(file, tokens, i, False, False, True)
                        return False
            elif tokens[i][0] == "RINT":
                if to_print:
                    if first_type is None:
                        first_type = "int"
                    else:
                        if first_type != "int":
                            generate_semantic_error(file, tokens, i)
                            return False
                if curr_var_type is not None and curr_var_type != "int":
                    generate_semantic_error(file, tokens, i)
                    return False
                if return_type is not None and return_type != "int":
                    generate_semantic_error(file, tokens, i, False, False, True)
                    return False
            elif tokens[i][0] == "RDBL":
                if to_print:
                    if first_type is None:
                        first_type = "double"
                    else:
                        if first_type != "double":
                            generate_semantic_error(file, tokens, i)
                            return False
                if curr_var_type is not None and curr_var_type != "double":
                    generate_semantic_error(file, tokens, i)
                    return False
                if return_type is not None and return_type != "double":
                    generate_semantic_error(file, tokens, i, False, False, True)
                    return False
            i += 1
            stack.pop()
            continue
        elif peek == "@":
            stack.pop()
            continue
        
        curr_token = tokens[i]
        row = int(peek)
        col = token_enum(curr_token)
        prod_to_add = ll_table[row][col]
        curr_prod = grammar[prod_to_add]
        stack.pop()
        
        if curr_prod == grammar[3]:
            is_fdec = True
        elif curr_prod == grammar[10]:
            is_decl = True
        elif curr_prod == grammar[19]: # var = expr
            is_var_eq_expr = True
        elif curr_prod == grammar[20]:
            is_if_or_while_statement = True
        elif curr_prod == grammar[26]:
            is_else_statement = True
        elif curr_prod == grammar[22]:
            is_print_statement = True
        elif curr_prod == grammar[23]:
            is_return_statement = True
            
        for j in range(len(curr_prod) - 1, -1, -1):
            stack.append(curr_prod[j])
            
        if is_fdec:
            stack.pop() # def
            i += 1
            
            func_type = tokens[i][0] # RINT or RDBL
            i += 1
            stack.pop() 
            
            func_iden = tokens[i][1] # iden
            i += 1
            stack.pop()
            
            # Check if func_iden in symbol table
            if find_iden_local(curr_table, func_iden):
                generate_semantic_error(file, tokens, i, True)
                return False
            
            curr_func = func_iden
            
            i += 1
            stack.pop() # (
            
            stack.pop() # params
            
            param_count = 0
            param_list = []
            # Create new symbol table
            curr_table.sub_table = SymbolTable(parent=curr_table)
            curr_table = curr_table.sub_table
            while tokens[i][0] != ")":
                if param_count != 0:
                    i += 1 # ,
                param_type = tokens[i][0] # type
                i += 1
                
                param_iden = tokens[i][1] # iden
                i += 1
                
                curr_table.table.append(STEntry(param_iden, param_type))
                param_list.append(param_type)
                param_count += 1
            curr_table.parent.table.append(STEntry(func_iden, func_type, param_count, param_list))
            
            is_fdec = False
            
        if is_decl:
            var_type = tokens[i][0] # type
            i += 1
            stack.pop()
            
            var_iden = tokens[i][1] # iden
            i += 1
            stack.pop()
            
            # Check if var_iden in symbol table (BEFORE APPENDING)
            if find_iden_local(curr_table, var_iden):
                generate_semantic_error(file, tokens, i, True)
                return False
            
            curr_table.table.append(STEntry(var_iden, var_type))
            
            
            
            while tokens[i][0] == ",":
                i += 1 # ,

                var_iden = tokens[i][1] # iden
                i += 1
                curr_table.table.append(STEntry(var_iden, var_type))
                
            is_decl = False

        if is_var_eq_expr:
            if not find_iden_global(curr_table, tokens[i][1]):
                generate_semantic_error(file, tokens, i, True)
                return False
            curr_var_type = get_iden_type(curr_table, tokens[i][1])
            stack.pop() # var
            i += 1
            
            stack.pop() # =
            i += 1
            
            end_temp_stack_len = len(stack) - 1 # Stores the length of the stack without var = expr
            
            
            is_var_eq_expr = False
            
        # Spontaneously combined the processing of if and while statements (for bexpr)
        if is_if_or_while_statement:
            for j in range(5):
                stack.pop() # if ( BEXPR ) then OR while ( BEXPR ) do
            i += 2
            j = i
            # Find the first iden type
            while tokens[j][0] != "then" and tokens[j][0] != "do":
                if tokens[j][0] == "iden":
                    bexpr_type = get_iden_type(curr_table, tokens[j][1])
                    break
                elif tokens[j][0] == "RINT":
                    bexpr_type = "int"
                    break
                elif tokens[j][0] == "RDBL":
                    bexpr_type = "double"
                    break
                j += 1
                    
            while tokens[i][0] != "then" and tokens[i][0] != "do":
                if tokens[i][0] == "iden":
                    if not find_iden_global(curr_table, tokens[i][1]) or get_iden_type(curr_table, tokens[i][1]) != bexpr_type:
                        generate_semantic_error(file, tokens, i, False)
                        return False
                elif tokens[i][0] == "RINT":
                    if bexpr_type != "int":
                        generate_semantic_error(file, tokens, i, False)
                        return False
                elif tokens[i][0] == "RDBL":
                    if bexpr_type != "double":
                        generate_semantic_error(file, tokens, i, False)
                        return False
                i += 1
            i += 1
            curr_table.sub_table = SymbolTable(parent=curr_table)
            curr_table = curr_table.sub_table
            
            is_if_or_while_statement = False
            
        if is_else_statement:
            i += 1
            stack.pop() # else
            
            # Delete local symbol table
            curr_table = curr_table.parent
            curr_table.sub_table = None
            
            # Create local symbol table
            curr_table.sub_table = SymbolTable(parent=curr_table)
            curr_table = curr_table.sub_table
            
            is_else_statement = False
        
        if is_print_statement:
            i += 1
            stack.pop()
            
            end_temp_stack_len = len(stack) - 1 # Stores the length of the stack without print expr
            
            first_type = None
            
            to_print = True
            
            is_print_statement = False
            
        if is_return_statement: # this is annoying
            i += 1
            stack.pop() # return
            
            end_temp_stack_len = len(stack) - 1 # Stores the length of the stack without return expr
            
            return_type = get_iden_type(curr_table, curr_func)

            is_return_statement = False
            
    return True

# Function for generating semantic errors (obv)
def generate_semantic_error(file, tokens, i, is_scope_error=False, is_param_num_error=False, is_return_type_error=False, is_param_type_error=False):
    print("Semantic Error at", i)
    print("See err_files/semantic_error_log.txt for more details")
    errfile = open("err_files/semantic_error_log.txt", "w")
    errfile.write(f"File \"{file}\".\n\tSemantic Error: ")
    
    prev_tokens = tokens[max(0, i-4):i]
    next_tokens = tokens[i+1:min(i+5, len(tokens))]
    
    for token in prev_tokens:
        errfile.write(token[1] + " ")
    errfile.write(f" >>> {tokens[i][1]} <<<  ")
    for token in next_tokens:
        errfile.write(token[1] + " ")
    errfile.write("\n")
    
    if is_scope_error:
        errfile.write(f"\tScope Error: Identifier {tokens[i][1]} not found in scope\n")
    elif is_param_num_error:
        errfile.write(f"\tScope Error: Number of parameters in function call does not match function definition\n")
    elif is_return_type_error:
        errfile.write(f"\tType Error: Return type does not match function return type\n")
    elif is_param_type_error:
        errfile.write(f"\tType Error: Input parameter type does not match function parameter type\n")
    else: 
        errfile.write(f"\tType Error: Token {tokens[i][1]} does not match expression type\n")
        
    return

# These classes are being treated like structs
class SymbolTable:
    def __init__(self, parent=None):
        self.table = [] # Array of STEntry
        self.sub_table = None # Stores a child SymbolTable
        self.parent = parent # Stores the parent SymbolTable
    def __str__(self):
        table_str = ""
        for i in range(len(self.table)):
            table_str += str(self.table[i]) + "\n"
        return table_str
    
class STEntry:
    def __init__(self, iden, type, num_params=None, params=None):
        self.iden = iden
        self.type = type
        self.num_params = num_params
        self.params = params
    def __str__(self):
        return f"{self.iden} {self.type} {self.num_params} {self.params}"