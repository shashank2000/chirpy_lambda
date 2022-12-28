from lark import Lark

with open('grammar.lark', 'r') as f:
    grammar = f.read()
#print(grammar)
json_parser = Lark(grammar, start='document')
with open('test1.camel', 'r') as f:
    text = f.read()
    print(json_parser.parse(text).pretty())
