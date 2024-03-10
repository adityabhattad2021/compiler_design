from collections import defaultdict
from tabulate import tabulate
from queue import LifoQueue


class Grammar:

    first = defaultdict(set)
    follow = defaultdict(set)
    start_symbol = ''

    def __init__(self, productions):
        self.productions = productions
        self.start_symbol = list(self.productions.keys())[0]
        self.first = self.calculate_first()
        self.follow = self.calculate_follow()

    def calculate_first(self):
        for nt, rhs in reversed(self.productions.items()):
            for alt in rhs:
                for s in alt:
                    if s.isupper():
                        if 'e' not in self.first[s]:
                            self.first[nt].update(self.first[s])
                            if 'e' in self.first[nt]:
                                self.first[nt].remove('e')
                            break
                        self.first[nt].update(self.first[s])
                    elif s != 'e':
                        self.first[nt].add(s)
                        if 'e' in self.first[nt]:
                            self.first[nt].remove('e')
                        break
                    else:
                        self.first[nt].add('e')
        return self.first

    def calculate_follow(self):

        self.follow[self.start_symbol].add('$')
        while True:
            old_follow = dict(self.follow)
            for nt, rhs in self.productions.items():
                for production in rhs:
                    for index, letter in enumerate(production[::-1]):
                        if index == 0:
                            if letter.isupper():
                                self.follow[letter].update(self.follow[nt])
                        else:
                            if letter.isupper():
                                temp = index-1
                                while temp >= 0:
                                    if list(reversed(production))[temp].islower():
                                        self.follow[letter].add(
                                            list(reversed(production))[temp])
                                        break
                                    else:
                                        if 'e' not in self.first[list(reversed(production))[temp]]:
                                            self.follow[letter].update(
                                                self.first[list(reversed(production))[temp]]
                                            )
                                            break
                                        else:
                                            self.follow[letter].update(
                                                self.first[list(reversed(production))[temp]]
                                            )
                                            self.follow[letter].remove('e')
                                    temp -= 1
            if old_follow == self.follow:
                break
        return self.follow

    def print_parsing_table(self):
        parsing_table,terminals,non_terminals = self.get_parsing_table()

        headers = sorted(list(terminals))
        rows = sorted(list(non_terminals))
        table = [[parsing_table[nt][t] for t in headers] for nt in rows]
        print(tabulate(table, headers=headers, showindex=rows, tablefmt='grid'))

    def get_parsing_table(self):
        terminals = set()
        non_terminals = set(self.productions.keys())
        for nt, rhs in self.productions.items():
            for alt in rhs:
                for symbol in alt:
                    if not symbol.isupper() and symbol != 'e':
                        terminals.add(symbol)
        terminals.add('$')

        terminals = sorted(list(terminals))
        non_terminals = sorted(list(non_terminals))
        parsing_table = defaultdict(lambda: defaultdict(str))
        for nt in non_terminals:
            temp_prod = self.productions[nt].copy()
            for t in terminals:
                for prod in temp_prod:
                    for letter in prod:
                        if letter == 'e' and (t in self.follow[nt] or t == '$'):
                            parsing_table[nt][t] = f"{nt}->e"
                            break
                        elif (letter == t and t in self.first[nt]):
                            parsing_table[nt][t] = f"{nt}->{prod}"
                            break
                        elif (letter.isupper() and t in self.first[letter]):
                            flag = False
                            for l in prod[:prod.index(letter)]:
                                if l.islower():
                                    flag=True
                                    break
                            if not flag:
                                parsing_table[nt][t] = f"{nt}->{prod}"
                                break
                        elif letter.isupper() and 'e' in self.first[letter] and len(prod)>1 and t in self.first[prod[prod.index(letter)+1]]:
                            parsing_table[nt][t] = f"{nt}->{prod}"
                            if 'e' not in self.first[letter]:
                                break       
                                
        return parsing_table,terminals,non_terminals
    
    def parse(self,string_to_parse:str,debug=False):
        parsing_table,_,_ = self.get_parsing_table()
        string_to_parse = string_to_parse[::-1]
        stack = LifoQueue()
        stack.put('$')
        string_to_parse='$'+string_to_parse
        stack.put(self.start_symbol)
        print(stack.queue)
        headers = ["Buffer","Stack","Actions"]
        table=[]
        while True:
            row=[]
            string_pointer = len(string_to_parse)-1
            top_of_stack = stack.get()
            dup_stack = list(stack.queue)
            dup_stack.append(top_of_stack)
            dup_stack=list(reversed(dup_stack))
            if string_to_parse[string_pointer]==top_of_stack=='$':
                print("String Accepted!")
                row=[string_to_parse,str(dup_stack),"Accepted"]
                table.append(row)
                break
            elif string_to_parse[string_pointer]==top_of_stack:
                row=[string_to_parse,str(dup_stack),"Match"]
                string_to_parse = string_to_parse[:-1]
            elif parsing_table[top_of_stack][string_to_parse[-1]] != '':
                production_rule:str=parsing_table[top_of_stack][string_to_parse[-1]]
                row=[string_to_parse,str(dup_stack),production_rule]
                production:str = production_rule.split('->')[1]
                for i in reversed(production):
                    stack.put(i)
            else:
                print("There was an error while parsing the string!")
                row=[string_to_parse,str(dup_stack),"No entry found in the table"]
                table.append(row)
                break
            table.append(row)
        if debug:
            print(tabulate(table, headers=headers,tablefmt="grid"))
        




    def print_sets(self):
        print("FIRST sets:")
        for nt, first_set in self.first.items():
            print(f"{nt}: {sorted(first_set)}")
        print("\nFOLLOW sets:")
        for nt, follow_set in self.follow.items():
            print(f"{nt}: {sorted(follow_set)}")


def main():

    a1 = {
        'S': ['aABb'],
        'A': ['c', 'e'],
        'B': ['d', 'e'],
    }
    a2 = {
        'S': ['Abc', 'ad'],
        'A': ['gS', 'Cr','e'],
        'C': ['f', 'p','e'],
    }

    grammar = Grammar(a2)
    grammar.print_sets()
    grammar.print_parsing_table()
    grammar.parse("frbc",debug=True)

if __name__ == "__main__":
    main()