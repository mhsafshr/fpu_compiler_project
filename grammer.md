program         = { statement } ;

statement       = assign_stmt
                | if_stmt
                | while_stmt
                | print_stmt
                | expr ;

assign_stmt     = IDENT "=" comparison ;

if_stmt         = "if" [ "(" ] comparison [ ")" ] "do" block "end" ;

while_stmt      = "while" [ "(" ] comparison [ ")" ] "do" block "end" ;

print_stmt      = "print" comparison ;

block           = { statement } "end" ;

comparison      = expr { ("<" | ">" | "<=" | ">=" | "==") comparison }? ;

expr            = term { ("+" | "-") term }* ;

term            = factor { ("*" | "/") factor }* ;

factor          = NUMBER
                | IDENT
                | "(" comparison ")" ;