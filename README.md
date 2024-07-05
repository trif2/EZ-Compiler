## EZ Compiler
This compiler was made for a course, and was divided into 4 phases: lexical analysis, syntax analysis, semantic analysis, and intermediate code generation

## Phase 1
Given a .cp file containing code, the file is turned into a list of tokens in lexical analysis. To create a list of tokens, the compiler has to iterate through the file character by character by using the transition table (think deterministic finite automata). 

![TTImage](https://github.com/trif2/EZ-Compiler/assets/72584875/e4239e16-9525-4746-a885-4325fca7fef7)

To put it simply, lexical_analysis() iterates through both the file and the transition table at the same time. If any errors are encountered, lexical_analysis() will attempt to find a matching character to continue along the transition table.

## Phase 2
From the list of tokens, syntax_analysis() attempts to analyze the syntactical structure (think grammar structure in languages). It uses a grammar file along with an LL1 (lookahead) table file. If any errors are found, syntax_analysis() will skip over tokens until it matches the grammar of the language

## Phase 3
Semantic analysis ensures that all variables are actually in scope when they are called, and checks that there are no type errors (like int = int + float, or wrong function parameter types). semantic_analysis() accomplishes this with the help of a few helper functions

## Phase 4
Finally, intermediate code, similar to ARM code, is generated since there are no errors (or errors have been removed). No error checking is required and the structure of generate_code() is essentially the same as semantic_analysis(); at certain tokens (like print, function decl/call, etc.), certain intermediate code will be written.

![IntCodeImage](https://github.com/trif2/EZ-Compiler/assets/72584875/1479513e-7298-4884-aee2-488703697b3f)

## Conclusion
Overall, this is a VERY superficial explanation of the code. This just gives an overview of what everything does.

## Instructions
To run, simply clone the repository and run some of the code in the testing folder, changing the file path at the top of EZSharp.py

## Missing Features
- Negative numbers (Phase 1)
- Nested boolean expressions (Phase 2)
- Labels not handled properly with bexpr for if and while (Phase 4)
