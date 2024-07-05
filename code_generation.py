from code_analysis import token_enum
# PHASE 4

# Used in process_expr for TAC
def operator_precedence(op):
    if op == "+" or op == "-":
        return 1
    elif op == "*" or op == "/" or op == "%":
        return 2
    return 0 # op == "(" or op == ")"

# Converts expr from infix to postfix, then postfix to TAC
def process_expr(tokens, start_register):
    id_count = 0
    for j in range(len(tokens)):
        if tokens[j][0] == "iden" or tokens[j][0] == "RINT" or tokens[j][0] == "RDBL":
            temp = tokens[j][1]
            id_count += 1
    if id_count == 1:
        return [f"t{start_register} = {temp}"]
    
    
    token_values = []
    tac_list = []
    curr_register = start_register
    # Check for any functions
    j = 0
    while j < len(tokens):
        if tokens[j][0] == "iden" and j < len(tokens) - 1:
            if tokens[j + 1][0] == "(":
                parentheses_count = 1
                
                if tokens[j+2][0] == ")":
                    param_count = 0
                else:
                    param_count = 1
                k = j + 2
                while parentheses_count > 0:
                    if param_count == 0:
                        k += 1
                        break
                    if tokens[k][0] == "(":
                        parentheses_count += 1
                    elif tokens[k][0] == ")":
                        parentheses_count -= 1
                    elif tokens[k][0] == "," and parentheses_count == 1:
                        param_count += 1
                    k += 1
                temp_tac = process_func(tokens[j:k], param_count, start_register)
                curr_register += len(temp_tac)
                tac_list.extend(temp_tac)
                token_values.append(f"t{curr_register - 1}")
                for l in range(j+1, k):
                    tokens.pop(j+1)
            else:
                token_values.append(tokens[j][1])
        else:
            token_values.append(tokens[j][1])
        j += 1
    
    postfix = []
    infix_stack = []
    
    # Convert infix to postfix because easy
    for j in range(len(token_values)):
        # funny line below
        if token_values[j] != "+" and token_values[j] != "-" and token_values[j] != "*" and token_values[j] != "/" and token_values[j] != "%" and token_values[j] != "(" and token_values[j] != ")":
            postfix.append(token_values[j])
        elif token_values[j] == "(":
            infix_stack.append(token_values[j])
        elif token_values[j] == ')':
            top = infix_stack.pop()
            while infix_stack and top != '(':
                postfix.append(top)
                top = infix_stack.pop()
        else:
            while (infix_stack and operator_precedence(token_values[j]) <= operator_precedence(infix_stack[-1])):
                postfix.append(infix_stack.pop())
            infix_stack.append(token_values[j])
    while infix_stack:
        postfix.append(infix_stack.pop())
    
    pf_stack = []
    for j in range(len(postfix)):
        if postfix[j] != "+" and postfix[j] != "-" and postfix[j] != "*" and postfix[j] != "/" and postfix[j] != "%":
            pf_stack.append(postfix[j])
        else:
            temp2 = pf_stack.pop()
            temp1 = pf_stack.pop()
            temp_op1 = postfix[j]
            tac_list.append(f"t{curr_register} = {temp1} {temp_op1} {temp2}")
            pf_stack.append(f"t{curr_register}")
            curr_register += 1
    return tac_list

# Returns the specific ARM instruction for the given relop
def get_relop_arm(op, is_not=False):
    if op == "<":
        if is_not:
            return "BGE"
        return "BLT"
    elif op == ">":
        if is_not:
            return "BLE"
        return "BGT"
    elif op == "<=":
        if is_not:
            return "BGT"
        return "BLE"
    elif op == ">=":
        if is_not:
            return "BLT"
        return "BGE"
    elif op == "==":
        if is_not:
            return "BNE"
        return "BEQ"
    elif op == "<>":
        if is_not:
            return "BEQ"
        return "BNE"

# Processes a function call and returns the ARM instructions
def process_func(tokens, param_count, start_register):
    curr_register = start_register
    parentheses_count = 1
    tac_list = []
    var_to_push = []
    if tokens[2][0] == ")":
        param_count = 0
    else:
        param_count = 1
    k = 2
    param_ptr = k
    while parentheses_count > 0:
        if param_count == 0:
            k += 1
            break
        if tokens[k][0] == "(":
            parentheses_count += 1
        elif tokens[k][0] == ")":
            parentheses_count -= 1
        elif tokens[k][0] == "," and parentheses_count == 1:
            temp_tac = process_expr(tokens[param_ptr:k], curr_register)
            tac_list.extend(temp_tac)
            curr_register += len(temp_tac)
            if len(temp_tac) > 1:
                var_to_push.append(temp_tac[-1].split()[0])
                param_count += 1
            param_ptr = k + 1
        k += 1
    if param_count > 0:
        temp_tac = process_expr(tokens[param_ptr:k-1], curr_register)
        tac_list.extend(temp_tac)
        curr_register += len(temp_tac)
        if len(temp_tac) > 1:
            var_to_push.append(temp_tac[-1].split()[0])
            param_count += 1
    
    for j in range(len(var_to_push)):
        tac_list.append(f"push {var_to_push[j]}")
    tac_list.append(f"t{curr_register} = BL {tokens[0][1]}")
    for j in range(len(var_to_push)):
        tac_list.append(f"pop {var_to_push[j]}")
    return tac_list

# Main function that generates intermediate code, tokens are processed similarly to semantic_analysis()
def generate_code(file, tokens, grammar, ll_table):
    arm_code = [] # List of ARM instructions in the form of strings
    arm_code.append("B main")
    min_register = 0
    
    stack = []
    stack.append("$")
    stack.append("0")
    i = 0

    is_fdec = False
    is_var_eq_expr = False
    is_if_statement = False
    is_while_statement = False
    is_print = False
    is_return = False
    
    end_temp_stack_len = 0
    processing_expr = False
    curr_expr = []
    curr_var = None
    to_print = False
    
    after_funcs = False
    
    if_count = 0
    else_count = 0
    while_count = 0
    cont_count = 0
    
    while len(stack) > 0 and i < len(tokens):
        curr_token = tokens[i]
        peek = stack[-1]
        
        if processing_expr and len(stack) == end_temp_stack_len:
            expr_list = process_expr(curr_expr, min_register)
            min_register += len(expr_list)
            if curr_var is not None and expr_list: # if var = expr
                expr_list.append(f"{curr_var} = {expr_list[-1].split()[0]}")
                # min_register += 1
            
            if to_print:
                expr_list.append(f"print {expr_list[-1].split()[0]}")
                min_register += 1
                to_print = False    
            
            for j in range(len(expr_list)):
                arm_code.append(expr_list[j])
            
            curr_var = None
            curr_expr = []
            processing_expr = False
            
        
        if peek == tokens[i][0]:
            if tokens[i][0] == "fed":
                # Functions with the string "exit_" in them are not allowed
                arm_code.append(f"exit_{curr_func}:")
                arm_code.append("pop {fp}")
                arm_code.append("pop {pc}")
                min_register = 0
                curr_func = None
            if tokens[i][0] == "else":
                arm_code.append(f"B cont{cont_count}")
                arm_code.append(f"else{else_count}:")
                else_count += 1
            if tokens[i][0] == "fi":
                arm_code.append(f"B cont{cont_count}")
                arm_code.append(f"cont{cont_count}:")
                cont_count += 1
            if tokens[i][0] == "od":
                arm_code.append(f"B loop{while_count}")
                while_count += 1
            if processing_expr:
                curr_expr.append(tokens[i])
                
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
        if prod_to_add == -1:
            print("hello")
        
        if stack == ["$", ".", "10", "5"] and not after_funcs:
            after_funcs = True
            arm_code.append("main:")
        
        curr_prod = grammar[prod_to_add]
        stack.pop()
        if curr_prod == grammar[3]: # fdec
            is_fdec = True
        if curr_prod == grammar[19]: # var = expr
            is_var_eq_expr = True
        if curr_prod == grammar[20]: # if statement
            is_if_statement = True
        if curr_prod == grammar[21]: # while statement
            is_while_statement = True
        if curr_prod == grammar[22]: # print
            is_print = True
        if curr_prod == grammar[23]: # return
            is_return = True
        
        for j in range(len(curr_prod) - 1, -1, -1):
            stack.append(curr_prod[j])
            
        if is_fdec:
            stack.pop() # def
            i += 1
            
            stack.pop() # type
            i += 1
            
            func_iden = tokens[i][1] # func_iden
            stack.pop()
            i += 1
            arm_code.append(f"{func_iden}:")
            arm_code.append("push {fp, lr}")
            
            curr_func = func_iden
            
            stack.pop() # (
            i += 1
            
            stack.pop() # params
            
            param_count = 0
            param_list = []
            
            while tokens[i][0] != ")":
                if param_count != 0:
                    i += 1 # ,
                i += 1 # type
                
                param_iden = tokens[i][1] # iden
                i += 1
                
                param_list.append(param_iden)
                param_count += 1
            for j in range(len(param_list)):
                arm_code.append(f"{param_list[j]} = fp + {8 + 4 * j}")
            
            is_fdec = False
            
                
        if is_var_eq_expr:
            curr_var = tokens[i][1]
            stack.pop() # var
            i += 1
            
            stack.pop() # =
            i += 1
            
            end_temp_stack_len = len(stack) - 1 # Stores the length of the stack without var = expr
            
            processing_expr = True
            curr_expr = []
            
            is_var_eq_expr = False
            
        if is_if_statement or is_while_statement:
            for j in range(5): # if ( BEXPR ) then OR while ( BEXPR ) do
                stack.pop() 
            curr_bexpr = []
            
            # Check if there is else
            if is_if_statement:
                has_else = False
                j = i
                while tokens[j][0] != "fi":
                    if tokens[j][0] == "else":
                        has_else = True
                        break
                    j += 1
            
            # Get tokens that correspond to bexpr, split it by relop, then process both into their own variables (TAC)
            j = i
            while tokens[j][0] != "then" and tokens[j][0] != "do":
                j += 1

            for k in range(i + 2, j):
                curr_bexpr.append(tokens[k])
            # bexpr_list = processBexpr(curr_bexpr, min_register)
            if is_if_statement:
                is_not = False
                x = 0
                if curr_bexpr[0][1] == "not":
                    x = 1
                    is_not = True
                arm_code.append(f"CMP {curr_bexpr[x][1]}, {curr_bexpr[x+2][1]}")
                arm_code.append(f"{get_relop_arm(curr_bexpr[x+1][1], is_not)} if{if_count}")
                if has_else:
                    arm_code.append(f"B else{else_count}")
                else:
                    arm_code.append(f"B cont{cont_count}")
                arm_code.append(f"if{if_count}:")
                if_count += 1
            if is_while_statement:
                is_not = False
                x = 0
                if curr_bexpr[0][1] == "not":
                    x = 1
                    is_not = True
                arm_code.append(f"loop{while_count}:")    
                arm_code.append(f"CMP {curr_bexpr[x][1]}, {curr_bexpr[x+2][1]}")
                arm_code.append(f"{get_relop_arm(curr_bexpr[x+1][1], not is_not)} cont{cont_count}")
                while_count += 1
                
            
            i = j + 1
            
            is_if_statement = False
            is_while_statement = False

        if is_print or is_return:
            i += 1
            stack.pop() # return
            
            end_temp_stack_len = len(stack) - 1 # Stores the length of the stack without return expr
            
            processing_expr = True
            
            curr_expr = []
            
            to_print = True
            
            is_print = False
            is_return = False

    with open("int_code.txt", "w") as fp:
        for i in range(len(arm_code)):
            fp.write(f"{arm_code[i]}\n")
    return True