import sys
from enum import Enum, auto
from copy import deepcopy
from typing import List, Dict, Set
from itertools import zip_longest
from itertools import chain, combinations

from copy import deepcopy
from typing import Dict, List, Set
from itertools import zip_longest

class Grammar:
    def __init__(self, grammar: Dict):
        self.non_terminals = set(grammar['nonterminals'])
        self.terminals = set(grammar['terminals'])
        self.start_symbol = grammar['start_symbol']
        self.productions = deepcopy(grammar['productions'])
        
    def _collect_terminals(self):
        """Собирает все терминальные символы из правил"""
        terminals = set()
        for rhs_list in self.productions.values():
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in self.non_terminals and symbol:
                        terminals.add(symbol)
        return terminals
    
    def check_language_existence(self):
        """
        Алгоритм 4.1: Проверка существования языка грамматики
        Возвращает True если язык существует (стартовый символ порождает терминальную строку)
        """
        print("\n2.0 Проверка существования языка грамматики (алгоритм 4.1):")
        N_prev = set()
        changed = True
        
        while changed:
            N_current = N_prev.copy()
            for A in self.non_terminals:
                for production in self.productions[A]:
                    # Проверяем все символы в продукции
                    all_valid = True
                    for symbol in production:
                        if symbol in self.non_terminals and symbol not in N_prev:
                            all_valid = False
                            break
                    
                    if all_valid:
                        N_current.add(A)
            
            changed = N_current != N_prev
            N_prev = N_current
        
        return self.start_symbol in N_prev
    
    #

    def eliminate_non_generating(self):
        """
        Алгоритм 4.2: Устранение нетерминалов, не порождающих терминальных строк
        
        После выполнения, self.productions и self.non_terminals будут очищены от бесполезных нетерминалов,
        которые не порождают терминальные строки.
        """
        print("\n2.1 Устранение нетерминалов, не порождающих терминальные строки (алгоритм 4.2):")
        non_generating_before = set(self.non_terminals) #Исходные нетерминалы
        
        generating = set() #Множество порождающих терминалов
        changed = True
        
        while changed:
            changed = False
            for A in self.non_terminals:
                if A not in generating:
                    for production in self.productions[A]:
                        if all((sym not in self.non_terminals) or (sym in generating) for sym in production):
                            generating.add(A)
                            changed = True
                            break
        
        new_productions = {}
        for A in generating:
            new_rhs = []
            for production in self.productions[A]:
                if all((sym not in self.non_terminals) or (sym in generating) for sym in production):
                    new_rhs.append(production)
            new_productions[A] = new_rhs
        
        non_generating_after = set(new_productions.keys())
        non_generating_removed = non_generating_before - non_generating_after
        
        # Вывод множества порождающих нетерминалов
        print(f" Множество порождающих нетерминалов: {', '.join(sorted(generating))}")
        
        # Вывод информации об устраненных нетерминалах
        if non_generating_removed:
            print(f" Устранены нетерминалы, не порождающие терминальные строки: {', '.join(sorted(non_generating_removed))}")
        else:
            print(" Нетерминалы, не порождающие терминальные строки, отсутствуют")
        
        # Вывод новых правил
        print(" Новые правила:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        self.productions = new_productions
        self.non_terminals = generating
        self.terminals = self._collect_terminals()

    def eliminate_unreachable(self):
        """
        Алгоритм 4.3: Устранение недостижимых символов
        
        Удаляет из грамматики символы (и правила), которые не достижимы из стартового символа.
        """
        print("\n2.2 Устранение недостижимых символов (алгоритм 4.3):")
        unreachable_before = set(self.non_terminals)
        
        reachable = set([self.start_symbol])
        changed = True
        
        while changed:
            changed = False
            for A in list(reachable):
                for production in self.productions.get(A, []):
                    for sym in production:
                        if sym in self.non_terminals and sym not in reachable:
                            reachable.add(sym)
                            changed = True
        
        # Удаляем недостижимые нетерминалы и правила
        new_productions = {}
        for A in reachable:
            new_rhs = []
            for production in self.productions[A]:
                if all((sym not in self.non_terminals) or (sym in reachable) for sym in production):
                    new_rhs.append(production)
            if new_rhs:
                new_productions[A] = new_rhs
        
        unreachable_after = set(new_productions.keys())
        unreachable_removed = unreachable_before - unreachable_after
        
        # Вывод множества достижимых нетерминалов
        print(f" Множество достижимых нетерминалов: {', '.join(sorted(reachable))}")
        
        # Вывод информации об устраненных нетерминалах
        if unreachable_removed:
            print(f" Устранены недостижимые символы: {', '.join(sorted(unreachable_removed))}")
        else:
            print(" Недостижимые символы отсутствуют")
        
        # Вывод новых правил
        print(" Новые правила:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        self.productions = new_productions
        self.non_terminals = set(new_productions.keys())
        self.terminals = self._collect_terminals()

    def remove_epsilon_rules(self):
        print("\n2.3 Устранение ε-правил (алгоритм 4.4):")
        nullable = set()
        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    if not body or all(sym in nullable for sym in body):
                        if head not in nullable:
                            nullable.add(head)
                            changed = True

        print(f" Множество ε-порождающих нетерминалов: {', '.join(sorted(nullable))}")

        new_productions = {}
        for head, bodies in self.productions.items():
            new_bodies = set()
            for body in bodies:
                if not body:  # Skip epsilon rules
                    continue
                nullable_indices = [i for i, sym in enumerate(body) if sym in nullable]
                for mask in range(1 << len(nullable_indices)):
                    new_body = []
                    include = [bool((mask >> i) & 1) for i in range(len(nullable_indices))]
                    for i, sym in enumerate(body):
                        if i not in nullable_indices or include[nullable_indices.index(i)]:
                            new_body.append(sym)
                    if new_body:
                        new_bodies.add(tuple(new_body))
            new_productions[head] = [list(b) for b in new_bodies]
        self.productions = new_productions

        print(" Новые правила:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        # Вывод стартового символа
        print(f" Стартовый символ: {self.start_symbol}")

    def eliminate_epsilon_rules(self):
        """
        Алгоритм 4.4: Устранение ε-правил
        
        Исключает ε-правила из грамматики, кроме допуска для стартового символа.
        """
        print("\n2.3 Устранение ε-правил (алгоритм 4.4):")
        # Подсчет ε-правил до устранения
        epsilon_rules_count_before = sum(1 for prods in self.productions.values() for prod in prods if prod == [])
        
        # Шаг 1. Найти множество ε-порождающих нетерминалов N
        N_prev = set(A for A, prods in self.productions.items() if [] in prods)
        changed = True
        
        while changed:
            changed = False
            for A in self.non_terminals:
                if A not in N_prev:
                    for production in self.productions[A]:
                        if all((sym in N_prev) or (sym not in self.non_terminals) for sym in production) and production:
                            N_prev.add(A)
                            changed = True
                            break
        
        nullable = N_prev
        
        # Вывод множества ε-порождающих нетерминалов
        print(f" Множество ε-порождающих нетерминалов: {', '.join(sorted(nullable))}")
        
        # Шаг 2. Переносим все правила кроме ε-правил
        new_productions = {}
        for A in self.non_terminals:
            new_rhs = [prod for prod in self.productions[A] if prod != []]
            new_productions[A] = new_rhs
        
        # Шаг 3. Добавляем новые правила, исключая всевозможные комбинации nullable символов
        def powerset(iterable):
            s = list(iterable)
            return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
        
        for A in list(new_productions.keys()):
            new_rules = set()
            for production in new_productions[A]:
                indices_nullable = [i for i, sym in enumerate(production) if sym in nullable]
                for to_remove in powerset(indices_nullable):
                    if to_remove == ():
                        continue
                    new_prod = [sym for i, sym in enumerate(production) if i not in to_remove]
                    if new_prod:
                        new_rules.add(tuple(new_prod))
            
            for rule in new_rules:
                if list(rule) not in new_productions[A]:
                    new_productions[A].append(list(rule))
        
        # Шаг 4. Обрабатываем стартовый символ
        S = self.start_symbol
        if S in nullable:
            if [] not in new_productions[S]:
                new_productions[S].append([])
        
        # Вывод новых правил
        print(" Новые правила:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        # Вывод стартового символа
        print(f" Стартовый символ: {self.start_symbol}")
        
        self.productions = new_productions
        self.non_terminals = set(new_productions.keys())
        self.terminals = self._collect_terminals()

    def eliminate_chain_rules(self):
        """
        Алгоритм 4.5: Устранение цепных правил
        
        Цепное правило: A -> B, где A и B - нетерминалы
        """
        print("\n2.4 Устранение цепных правил (алгоритм 4.5):")
        # Подсчет цепных правил до устранения
        chain_rules_count_before = sum(1 for nt, prods in self.productions.items() 
                                     for prod in prods 
                                     if len(prod) == 1 and prod[0] in self.non_terminals)
        
        # Шаг 1: для каждого A вычислить множество N_A
        N_sets = {}
        for A in self.non_terminals:
            N_current = set([A])
            changed = True
            while changed:
                changed = False
                to_add = set()
                for B in N_current:
                    for production in self.productions.get(B, []):
                        if len(production) == 1 and production[0] in self.non_terminals:
                            C = production[0]
                            if C not in N_current:
                                to_add.add(C)
                if to_add:
                    N_current |= to_add
                    changed = True
            N_sets[A] = N_current
        
        # Шаг 2: формируем новые правила
        new_productions = {}
        for A in self.non_terminals:
            new_rhs = []
            for B in N_sets[A]:
                for production in self.productions.get(B, []):
                    if not (len(production) == 1 and production[0] in self.non_terminals):
                        if production not in new_rhs:
                            new_rhs.append(production)
            new_productions[A] = new_rhs
        
        # Вывод множества нетерминалов без цепных правил
        print(f" Множество нетерминалов без цепных правил: {', '.join(sorted(new_productions.keys()))}")
        
        # Вывод новых правил
        print(" Новые правила:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        self.productions = new_productions
        self.non_terminals = set(new_productions.keys())
        self.terminals = self._collect_terminals()

    def eliminate_left_factoring(self):
        """
        Алгоритм 4.6: Устранение левой факторизации правил.
        
        Для каждого нетерминала находим группы правил с общими префиксами
        и факторизуем их, создавая новые нетерминалы.
        """
        print("\n2.5 Устранение левой факторизации (алгоритм 4.6):")
        # Сохраняем количество продукций до обработки
        productions_count_before = sum(len(prods) for prods in self.productions.values())
        nonterminals_count_before = len(self.non_terminals)
        
        import copy
        new_productions = copy.deepcopy(self.productions)
        changed = True
        new_nt_index = 0
        
        def longest_common_prefix(productions):
            if not productions:
                return []
            prefix = productions[0]
            for prod in productions[1:]:
                i = 0
                while i < min(len(prefix), len(prod)) and prefix[i] == prod[i]:
                    i += 1
                prefix = prefix[:i]
                if prefix == []:
                    break
            return prefix
        
        while changed:
            changed = False
            for A in list(new_productions.keys()):
                prods = new_productions[A]
                if len(prods) < 2:
                    continue
                
                prefix_groups = {}
                for prod in prods:
                    key = prod[0] if prod else None
                    prefix_groups.setdefault(key, []).append(prod)
                
                for key, group in prefix_groups.items():
                    if len(group) < 2:
                        continue
                    prefix = longest_common_prefix(group)
                    if len(prefix) > 0:
                        new_nt = f"{A}_fact{new_nt_index}"
                        new_nt_index += 1
                        changed = True
                        
                        new_rhs = []
                        for prod in prods:
                            if prod in group:
                                continue
                            new_rhs.append(prod)
                        new_rhs.append(prefix + [new_nt])
                        
                        fact_prods = []
                        plen = len(prefix)
                        for prod in group:
                            tail = prod[plen:]
                            if tail == []:
                                tail = [[]]
                            fact_prods.append(tail)
                        
                        fact_prods_expanded = []
                        for fprod in fact_prods:
                            if fprod == [[]]:
                                fact_prods_expanded.append([])
                            else:
                                fact_prods_expanded.append(fprod)
                        
                        new_productions[A] = new_rhs
                        new_productions[new_nt] = fact_prods_expanded
                        break
                if changed:
                    break
        
        # Вывод множества нетерминалов
        print(f" Множество нетерминалов: {', '.join(sorted(new_productions.keys()))}")
        
        # Вывод новых правил без одинаковых префиксов
        print(" Новые правила без одинаковых префиксов:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        self.productions = new_productions
        self.non_terminals = set(new_productions.keys())
        self.terminals = self._collect_terminals()

    def eliminate_immediate_left_recursion(self):
        """
        Устранение прямой левой рекурсии (алгоритм 4.7).
        Для каждого нетерминала X ищем правила вида X -> X alpha (левая рекурсия)
        и правила X -> beta (без левой рекурсии).
        Создаем новый нетерминал X' и преобразуем правила:
        
        X  -> beta X'
        X' -> alpha X' | ε
        """
        print("\n2.6 Устранение левой рекурсии (алгоритм 4.7):")
        # Сохраняем количество продукций и нетерминалов до обработки
        productions_count_before = sum(len(prods) for prods in self.productions.values())
        nonterminals_count_before = len(self.non_terminals)
        
        import copy
        new_productions = {}
        new_nt_index = 0
        
        for A in self.productions:
            prods = self.productions[A]
            
            recursive = []
            non_recursive = []
            
            for prod in prods:
                if len(prod) > 0 and prod[0] == A:
                    recursive.append(prod[1:])
                else:
                    non_recursive.append(prod)
            
            if recursive:
                new_nt = f"{A}_rec{new_nt_index}"
                new_nt_index += 1
                
                new_productions[A] = [beta + [new_nt] for beta in non_recursive]
                new_productions[new_nt] = [alpha + [new_nt] for alpha in recursive]
                new_productions[new_nt].append([])
                
            else:
                new_productions[A] = prods
        
        # Вывод множества нетерминалов
        print(f" Множество нетерминалов: {', '.join(sorted(new_productions.keys()))}")
        
        # Вывод новых правил без прямой левой рекурсии
        print(" Новые правила без прямой левой рекурсии:")
        for A in sorted(new_productions.keys()):
            productions = new_productions[A]
            print(f"  {A} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
        
        self.productions = new_productions
        self.non_terminals = set(new_productions.keys())
        self.terminals = self._collect_terminals()

    def print_grammar(self):
        """Выводит текущие правила грамматики в читаемом формате"""
        print("\nТекущая грамматика:")
        for non_terminal in sorted(self.productions.keys()):
            productions = self.productions[non_terminal]
            print(f"{non_terminal} -> ", end="")
            for i, prod in enumerate(productions):
                if i > 0:
                    print(" | ", end="")
                print(" ".join(prod) if prod else "ε", end="")
            print()
            
        print(f"\nСтартовый символ: {self.start_symbol}")
        print(f"Количество нетерминалов: {len(self.non_terminals)}")
        print(f"Количество терминалов: {len(self.terminals)}")

class CFGNormalizer:
    def __init__(self, grammar: Dict):
        self.nonterminals = set(grammar['nonterminals'])
        self.terminals = set(grammar['terminals'])
        self.start_symbol = grammar['start_symbol']
        self.productions = deepcopy(grammar['productions'])

    def normalize(self) -> Dict:
        if not self.language_exists():
            raise ValueError("The language of the grammar is empty.")

        self.remove_useless_symbols()
        self.remove_unreachable_symbols()
        self.remove_epsilon_rules()
        self.remove_chain_rules()
        self.left_factor()
        self.remove_direct_left_recursion()

        return {
            "nonterminals": self.nonterminals,
            "terminals": self.terminals,
            "productions": self.productions,
            "start_symbol": self.start_symbol
        }

    def language_exists(self) -> bool:
        generating = set()
        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    if all(sym in generating or sym in self.terminals for sym in body):
                        if head not in generating:
                            generating.add(head)
                            changed = True
        return self.start_symbol in generating

    def remove_useless_symbols(self):
        generating = set()
        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    if all(sym in generating or sym in self.terminals for sym in body):
                        if head not in generating:
                            generating.add(head)
                            changed = True

        self.productions = {h: [b for b in bs if all(sym in generating or sym in self.terminals for sym in b)]
                          for h, bs in self.productions.items() if h in generating}
        self.nonterminals &= generating

    def remove_unreachable_symbols(self):
        reachable = {self.start_symbol}
        changed = True
        while changed:
            changed = False
            for head in list(reachable):
                for body in self.productions.get(head, []):
                    for sym in body:
                        if sym in self.nonterminals and sym not in reachable:
                            reachable.add(sym)
                            changed = True
        self.productions = {h: [b for b in bs if all(sym in self.terminals or sym in reachable for sym in b)]
                          for h, bs in self.productions.items() if h in reachable}
        self.nonterminals &= reachable

    def remove_epsilon_rules(self):
        nullable = set()
        changed = True
        while changed:
            changed = False
            for head, bodies in self.productions.items():
                for body in bodies:
                    if not body or all(sym in nullable for sym in body):
                        if head not in nullable:
                            nullable.add(head)
                            changed = True

        new_productions = {}
        for head, bodies in self.productions.items():
            new_bodies = set()
            for body in bodies:
                if not body:  # Skip epsilon rules
                    continue
                nullable_indices = [i for i, sym in enumerate(body) if sym in nullable]
                for mask in range(1 << len(nullable_indices)):
                    new_body = []
                    include = [bool((mask >> i) & 1) for i in range(len(nullable_indices))]
                    for i, sym in enumerate(body):
                        if i not in nullable_indices or include[nullable_indices.index(i)]:
                            new_body.append(sym)
                    if new_body:
                        new_bodies.add(tuple(new_body))
            new_productions[head] = [list(b) for b in new_bodies]
        self.productions = new_productions

    def remove_chain_rules(self):
        chains = {nt: {nt} for nt in self.nonterminals}
        changed = True
        while changed:
            changed = False
            for nt in self.nonterminals:
                for body in self.productions.get(nt, []):
                    if len(body) == 1 and body[0] in self.nonterminals:
                        if body[0] not in chains[nt]:
                            chains[nt].add(body[0])
                            changed = True

        new_productions = {}
        for nt in self.nonterminals:
            new_bodies = []
            for target in chains[nt]:
                for body in self.productions.get(target, []):
                    if not (len(body) == 1 and body[0] in self.nonterminals):
                        if body not in new_bodies:
                            new_bodies.append(body)
            new_productions[nt] = new_bodies
        self.productions = new_productions

    def left_factor(self):
        def longest_common_prefix(sequences):
            result = []
            for parts in zip_longest(*sequences):
                if all(p == parts[0] for p in parts if p is not None):
                    result.append(parts[0])
                else:
                    break
            return result

        updated = True
        counter = 1
        while updated:
            updated = False
            new_productions = {}
            for head, bodies in self.productions.items():
                if len(bodies) < 2:
                    new_productions[head] = bodies
                    continue
                
                prefix = longest_common_prefix(bodies)
                if prefix:
                    updated = True
                    common_len = len(prefix)
                    suffixes = []
                    for body in bodies:
                        if body[:common_len] == prefix:
                            suffixes.append(body[common_len:] if body[common_len:] else [])
                    
                    new_nt = f"{head}_fact{counter}"
                    while new_nt in self.nonterminals:
                        counter += 1
                        new_nt = f"{head}_fact{counter}"
                    
                    self.nonterminals.add(new_nt)
                    new_productions[head] = [prefix + [new_nt]]
                    new_productions[new_nt] = suffixes
                    counter += 1
                else:
                    new_productions[head] = bodies
            self.productions = new_productions

    def remove_direct_left_recursion(self):
        new_productions = {}
        new_nonterminals = set(self.nonterminals)
        
        for A in list(self.nonterminals):
            alpha = []
            beta = []
            for body in self.productions.get(A, []):
                if body and body[0] == A:
                    alpha.append(body[1:])
                else:
                    beta.append(body)
            
            if alpha:
                A_prime = A + "'"
                while A_prime in new_nonterminals:
                    A_prime += "'"
                
                new_nonterminals.add(A_prime)
                new_productions[A] = [b + [A_prime] for b in beta] if beta else [[A_prime]]
                new_productions[A_prime] = [a + [A_prime] for a in alpha] + [[]]
            else:
                new_productions[A] = self.productions.get(A, [])
        
        self.productions = new_productions
        self.nonterminals = new_nonterminals




# Типы токенов
class TokenType(Enum):
    PROGRAM = auto()
    VAR = auto()
    BEGIN = auto()
    END = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    FOR = auto()
    TO = auto()
    DO = auto()
    WHILE = auto()
    READ = auto()
    WRITE = auto()
    ASS = auto()  # оператор присваивания
    ID = auto()
    INTEGER = auto()    # %
    FLOAT = auto()  # !
    BOOLEAN = auto()    # $
    LITERAL = auto()
    SEMICOLON = auto()  # ;
    COLON = auto()     # :
    COMMA = auto()     # ,
    DOT = auto()       # .
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    # Операции
    OP_REL = auto()    # < > = <= >=
    OP_ADD = auto()    # + - or
    OP_MUL = auto()    # * / and
    OP_UN = auto()     # not
    EOF = auto()

# Класс токена
class Token:
    def __init__(self, type: TokenType, value: int | str | None =None ):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

# Лексический анализатор
class Lexer:
    def __init__(self, text : str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
    
    def error(self):
        raise Exception(self.current_char, "Недопустимый символ")
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        while self.current_char != '}' and self.current_char is not None:
            self.advance()
        if self.current_char == '}':
            self.advance()
    
    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += '.'
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(TokenType.LITERAL, float(result))
        return Token(TokenType.LITERAL, int(result))
    
    def _id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # Ключевые слова
        keywords = {
            'program': TokenType.PROGRAM,
            'var': TokenType.VAR,
            'begin': TokenType.BEGIN,
            'end': TokenType.END,
            'if': TokenType.IF,
            'then': TokenType.THEN,
            'else': TokenType.ELSE,
            'for': TokenType.FOR,
            'to': TokenType.TO,
            'do': TokenType.DO,
            'while': TokenType.WHILE,
            'read': TokenType.READ,
            'write': TokenType.WRITE,
            'ass': TokenType.ASS,
            'or': TokenType.OP_ADD,
            'and': TokenType.OP_MUL,
            'not': TokenType.OP_UN,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN
        }
        
        return Token(keywords.get(result.lower(), TokenType.ID), result)
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self._id()
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';')
            
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON, ':')
            
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',')
            
            if self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT, '.')
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')
            
            if self.current_char == '%':
                self.advance()
                return Token(TokenType.INTEGER, '%')
            
            if self.current_char == '!':
                self.advance()
                return Token(TokenType.FLOAT, '!')
            
            if self.current_char == '$':
                self.advance()
                return Token(TokenType.BOOLEAN, '$')

            # Операции отношения
            if self.current_char in ('<', '>', '='):
                prev_char = self.current_char
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.OP_REL, prev_char + '=')
                return Token(TokenType.OP_REL, prev_char)
            
            # Операции сложения
            if self.current_char in ('+', '-'):
                char = self.current_char
                self.advance()
                return Token(TokenType.OP_ADD, char)
            
            # Операции умножения
            if self.current_char in ('*', '/'):
                char = self.current_char
                self.advance()
                return Token(TokenType.OP_MUL, char)
            
            self.error()
        
        return Token(TokenType.EOF, None)

class Symbol:
    def __init__(self, name, type_, value=None):
        self.name = name
        self.type = type_  # %, ! или $
        self.value = value
    
    def __repr__(self):
        return f"Symbol(name={self.name}, type={self.type}, value={self.value})"

class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]  # Реализация методом цепочек

    def _hash(self, key):
        """Простая хеш-функция для строковых ключей"""
        return sum(ord(char) for char in key) % self.size

    def insert(self, key, value):
        """Вставка или обновление значения по ключу"""
        hash_key = self._hash(key)
        bucket = self.table[hash_key]
        
        # Проверяем, есть ли уже такой ключ в цепочке
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        # Если ключ не найден, добавляем новую пару
        bucket.append((key, value))

    def get(self, key):
        """Получение значения по ключу"""
        hash_key = self._hash(key)
        bucket = self.table[hash_key]
        
        for k, v in bucket:
            if k == key:
                return v
        return None

    def delete(self, key):
        """Удаление значения по ключу"""
        hash_key = self._hash(key)
        bucket = self.table[hash_key]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return
        raise KeyError(key)

    def __contains__(self, key):
        """Проверка наличия ключа"""
        return self.get(key) is not None

class SymbolTable:
    def __init__(self):
        self.table = HashTable()  # Используем нашу хеш-таблицу

    def define(self, symbol):
        """Добавляем символ в таблицу"""
        if symbol.name in self.table:  # Используем __contains__ из HashTable
            raise NameError(f"Переменная {symbol.name} уже объявлена")
        self.table.insert(symbol.name, symbol)

    def lookup(self, name):
        """Поиск символа по имени"""
        return self.table.get(name)

# Абстрактное синтаксическое дерево
class AST:
    pass

class Program(AST):
    def __init__(self, declarations , compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement

class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Compound(AST):
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class If(AST):
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Literal(AST):
    def __init__(self, token):
        self.token = token
        if token.type == TokenType.BOOLEAN:
            if token.value == 'true':
                self.value = True
            else:
                self.value = False
        else:
            self.value = token.value

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class NoOp(AST):
    pass

class Write(AST):
    def __init__(self, expressions):
        self.expressions = expressions

# Парсер
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Синтаксическая ошибка")
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def program(self):
        """program : PROGRAM VAR (variable_declaration SEMICOLON)+ BEGIN compound_statement END DOT"""
        self.eat(TokenType.PROGRAM)
        self.eat(TokenType.VAR)
        declarations = []
        
        while self.current_token.type == TokenType.ID:
            var_decl = self.variable_declaration()
            declarations.extend(var_decl)
            self.eat(TokenType.SEMICOLON)
        
        self.eat(TokenType.BEGIN)
        compound_statement = self.compound_statement()
        self.eat(TokenType.END)
        self.eat(TokenType.DOT)
        
        return Program(declarations, compound_statement)
    
    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)]
        self.eat(TokenType.ID)
        
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(TokenType.ID)
        
        self.eat(TokenType.COLON)
        
        type_node = self.type_spec()
        return [VarDecl(var_node, type_node) for var_node in var_nodes]
    
    def type_spec(self):
        """type_spec : % | ! | $"""
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
        elif token.type == TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
        else:
            self.error()
        return Type(token)
    
    def compound_statement(self):
        """compound_statement : statement (SEMICOLON statement)*"""
        compound = Compound()
        compound.children.append(self.statement())
        
        while self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            compound.children.append(self.statement())
        
        return compound
    
    def statement(self):
        if self.current_token.type == TokenType.BEGIN:
            return self.compound_statement()
        elif self.current_token.type == TokenType.ID:
            return self.assignment_statement()
        elif self.current_token.type == TokenType.IF:
            return self.if_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.for_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_statement()
        elif self.current_token.type == TokenType.READ:
            return self.read_statement()
        elif self.current_token.type == TokenType.WRITE:
            return self.write_statement()
        else:
            return self.empty()

    def if_statement(self):
        self.eat(TokenType.IF)
        condition = self.expr()
        self.eat(TokenType.THEN)
        true_branch = self.statement()
        
        false_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            false_branch = self.statement()
        
        return If(condition, true_branch, false_branch)

    def assignment_statement(self):
        """assignment_statement : variable ASS expr"""
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASS)
        right = self.expr()  # Вот ключевое изменение - используем expr() вместо statement()
        return Assign(left, token, right)

    def expr(self):
        """expr : simple_expr ((< | = | > | <= | >=) simple_expr)?"""
        node = self.simple_expr()
        
        while self.current_token.type == TokenType.OP_REL:
            token = self.current_token
            self.eat(TokenType.OP_REL)
            node = BinOp(left=node, op=token, right=self.simple_expr())
        
        return node

    def simple_expr(self):
        """simple_expr : term ((+ | - | or) term)*"""
        node = self.term()
        
        while self.current_token.type == TokenType.OP_ADD:
            token = self.current_token
            self.eat(TokenType.OP_ADD)
            node = BinOp(left=node, op=token, right=self.term())
        
        return node

    def term(self):
        """term : factor ((* | / | and) factor)*"""
        node = self.factor()
        
        while self.current_token.type == TokenType.OP_MUL:
            token = self.current_token
            self.eat(TokenType.OP_MUL)
            node = BinOp(left=node, op=token, right=self.factor())
        
        return node

    def factor(self):
        """factor : (+ | - | not) factor | variable | literal | ( expr )"""
        token = self.current_token
        
        if token.type == TokenType.OP_ADD and token.value in ('+', '-'):
            self.eat(TokenType.OP_ADD)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == TokenType.OP_UN:
            self.eat(TokenType.OP_UN)
            return UnaryOp(op=token, expr=self.factor())
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.ID:
            return self.variable()
        elif token.type == TokenType.LITERAL:
            return self.literal()
        elif token.type == TokenType.BOOLEAN:  # Добавьте эту ветку
            node = Literal(self.current_token)
            self.eat(TokenType.BOOLEAN)
            return node

        else:
            self.error()
    
    def literal(self):
        node = Literal(self.current_token)
        self.eat(TokenType.LITERAL)
        return node
    
    def variable(self):
        """variable : ID"""
        node = Var(self.current_token)
        self.eat(TokenType.ID)
        return node
    
    def write_statement(self):
        """write_statement : WRITE LPAREN expr (COMMA expr)* RPAREN"""
        self.eat(TokenType.WRITE)
        self.eat(TokenType.LPAREN)
        
        # Собираем все выражения для вывода
        expressions = []
        expressions.append(self.expr())
        
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            expressions.append(self.expr())
        
        self.eat(TokenType.RPAREN)
        return Write(expressions)

    def empty(self):
        return NoOp()
    
    def parse(self):
        node = self.program()
        print(node)
        if self.current_token.type != TokenType.EOF:
            self.error()
        return node

    def for_statement(self):
        self.eat(TokenType.FOR)
        assign = self.assignment_statement()
        self.eat(TokenType.TO)
        final_value = self.expr()
        self.eat(TokenType.DO)
        body = self.statement()
        return (assign, final_value, body)

    def while_statement(self):
        self.eat(TokenType.WHILE)
        condition = self.expr()
        self.eat(TokenType.DO)
        body = self.statement()
        return (condition, body)
    
    def read_statement(self):
        self.eat(TokenType.READ)
        self.eat(TokenType.LPAREN)
        vars = [self.variable()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            vars.append(self.variable())
        self.eat(TokenType.RPAREN)
        return vars




# Интерпретатор
class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.symtab = SymbolTable()
    
    def interpret(self):
        tree = self.parser.parse()
        self.visit(tree)
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception(f'Нет метода visit_{type(node).__name__}')
    
    def visit_Program(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)
    
    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        var_type = node.type_node.value
        
        if self.symtab.lookup(var_name) is not None:
            raise NameError(f"Переменная '{var_name}' уже объявлена")
        
        if var_type == '%':
            default_value = 0
        elif var_type == '!':
            default_value = 0.0
        elif var_type == '$':
            default_value = False
        else:
            raise TypeError(f"Неизвестный тип '{var_type}'")
        
        self.symtab.define(Symbol(var_name, var_type, default_value))
    
    def visit_Type(self, node):
        pass
    
    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)
    
    def visit_Assign(self, node):
        var_name = node.left.value
        value = self.visit(node.right)
        symbol = self.symtab.lookup(var_name)
        if symbol is None:
            raise NameError(f"Переменная '{var_name}' не объявлена")
        symbol.value = value  # Просто присваиваем значение напрямую

    def visit_Var(self, node):
        var_name = node.value
        symbol = self.symtab.lookup(var_name)
        if symbol is None:
            raise NameError(f"Идентификатор не найден: {var_name}")
        return symbol.value
    
    def visit_Literal(self, node):
        return node.value
    
    def visit_Write(self, node):
        results = []
        for expr in node.expressions:
            value = self.visit(expr)
            results.append(str(value))
        print(' '.join(results))

    def visit_BinOp(self, node):
        """Обработка бинарных операций"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Проверка типов (можно вынести в отдельный метод)
        if isinstance(left, bool) or isinstance(right, bool):
            if node.op.type != TokenType.OP_MUL or node.op.value != 'and':
                if node.op.type != TokenType.OP_ADD or node.op.value != 'or':
                    raise TypeError("Логические операции поддерживают только 'and' и 'or'")
        
        # Операции группы умножения (*, /, and)
        if node.op.type == TokenType.OP_MUL:
            if node.op.value == '*':
                return left * right
            elif node.op.value == '/':
                if right == 0:
                    raise ZeroDivisionError("Деление на ноль")
                return left / right
            elif node.op.value == 'and':
                return left and right
        
        # Операции группы сложения (+, -, or)
        elif node.op.type == TokenType.OP_ADD:
            if node.op.value == '+':
                return left + right
            elif node.op.value == '-':
                return left - right
            elif node.op.value == 'or':
                return left or right
        
        # Операции группы отношения (<, >, =, <=, >=)
        elif node.op.type == TokenType.OP_REL:
            if node.op.value == '<':
                return left < right
            elif node.op.value == '<=':
                return left <= right
            elif node.op.value == '>':
                return left > right
            elif node.op.value == '>=':
                return left >= right
            elif node.op.value == '=':
                return left == right
        
        raise ValueError(f"Неизвестный бинарный оператор: {node.op.value}")

    def visit_UnaryOp(self, node):
        """Обработка унарных операций: +, -, not"""
        if node.op.type == TokenType.OP_UN and node.op.value == 'not':
            return not self.visit(node.expr)
        elif node.op.type == TokenType.OP_ADD and node.op.value == '+':
            return +self.visit(node.expr)
        elif node.op.type == TokenType.OP_ADD and node.op.value == '-':
            return -self.visit(node.expr)
        else:
            raise ValueError(f"Неизвестный унарный оператор: {node.op.value}")

    def visit_NoOp(self, node):
        pass

    def visit_If(self, node):
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.true_branch)
        elif node.false_branch is not None:
            self.visit(node.false_branch)

    def visit_tuple(self, node):
        if len(node) == 3:
            # for: (assign, final_value, body)
            assign, final_value_expr, body = node
            self.visit(assign)
            var_name = assign.left.value
            final_value = self.visit(final_value_expr)
            while self.symtab.lookup(var_name).value <= final_value:
                self.visit(body)
                self.symtab.lookup(var_name).value += 1
        elif len(node) == 2:
            # while: (condition, body)
            condition, body = node
            while self.visit(condition):
                self.visit(body)

    def visit_list(self, node):
        for var in node:
            var_name = var.value
            symbol = self.symtab.lookup(var_name)
            if symbol is None:
                raise NameError(f"Переменная '{var_name}' не объявлена")
            # тестово присваиваем 1
            symbol.value = 1

    

def main():
    grammar1 = {
    "nonterminals": {
        "программа", "описание", "тело", "оператор", "присваивания", "условный",
        "цикла", "цикла_фиксированный", "составной", "ввода", "вывода", "выражение", 
        "сумма", "произведение", "множитель", "унарное", "идентификатор", "число", 
        "логическая_константа", "описание_хвост", "оператор_список", "тип",
        "знак_сравнения", "сумма_хвост", "произведение_хвост", "ид_хвост",
        "ввода_хвост", "вывода_хвост", "буква", "цифра", "комментарий"
    },
    "terminals": {
        "program", "var", "begin", "end", "int", "bool", "read", "write", "if", "then",
        "else", "while", "do", "for", "to", "true", "false", "not", ":=", "=", "<", ">", 
        "<=", ">=", "+", "-", "*", "/", "or", "and", "(", ")", ",", ":", ";", ".", "a", 
        "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", 
        "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", 
        "7", "8", "9", "{", "}"
    },
    "start_symbol": "программа",
    "productions": {
        # Основные конструкции
        "программа": [["program", "описание", ";", "тело", "."], ["комментарий", "program", "описание", ";", "тело", "."]],
        "описание": [["var", "идентификатор", "описание_хвост", ":", "тип"]],
        "описание_хвост": [["идентификатор", "описание_хвост"], []],
        "тип": [["int"], ["bool"]],
        
        # Тело и операторы
        "тело": [["begin", "оператор_список", "end"], ["комментарий", "begin", "оператор_список", "end"]],
        "оператор_список": [["оператор", ";", "оператор_список"], ["оператор"]],
        "оператор": [["присваивания"], ["условный"], ["цикла"], ["цикла_фиксированный"], ["составной"], ["ввода"], ["вывода"], ["комментарий"]],
        
        # Операторы
        "присваивания": [["идентификатор", ":=", "выражение"]],
        "условный": [["if", "выражение", "then", "оператор", "else", "оператор"], ["if", "выражение", "then", "оператор"]],
        "цикла": [["while", "выражение", "do", "оператор"]],
        "цикла_фиксированный": [["for", "присваивания", "to", "выражение", "do", "оператор"]],
        "составной": [["begin", "оператор_список", "end"]],
        "ввода": [["read", "(", "идентификатор", "ввода_хвост", ")"]],
        "ввода_хвост": [[",", "идентификатор", "ввода_хвост"], []],
        "вывода": [["write", "(", "выражение", "вывода_хвост", ")"]],
        "вывода_хвост": [[",", "выражение", "вывода_хвост"], []],
        
        # Выражения
        "выражение": [["унарное"], ["сумма"], ["сумма", "знак_сравнения", "сумма"]],
        "унарное": [["not", "множитель"]],
        "знак_сравнения": [["="], ["<"], [">"], ["<="], [">="]],
        
        # Арифметические выражения
        "сумма": [["произведение", "сумма_хвост"]],
        "сумма_хвост": [["операция_сложения", "произведение", "сумма_хвост"], []],
        "операция_сложения": [["+"], ["-"], ["or"]],
        
        "произведение": [["множитель", "произведение_хвост"]],
        "произведение_хвост": [["операция_умножения", "множитель", "произведение_хвост"], []],
        "операция_умножения": [["*"], ["/"], ["and"]],
        
        "множитель": [["идентификатор"], ["число"], ["логическая_константа"], ["(", "выражение", ")"]],
        
        # Лексемы
        "идентификатор": [["буква", "ид_хвост"]],
        "ид_хвост": [["буква", "ид_хвост"], ["цифра", "ид_хвост"], []],
        "число": [["цифра", "число"], ["цифра"]],
        "логическая_константа": [["true"], ["false"]],
        "буква": [[c] for c in "abcdefghijklmnopqrstuvwxyz"],
        "цифра": [[d] for d in "0123456789"],
        
        # Комментарии
        "комментарий": [["{", "текст_комментария", "}"]],
        "текст_комментария": [["символ", "текст_комментария"], []],
        "символ": [[c] for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ \t\n"]
    }
}


    grammar222 = Grammar(grammar1)
    grammar222.print_grammar()
    grammar222.check_language_existence()
    grammar222.remove_epsilon_rules()
    grammar222.print_grammar()
    grammar222.eliminate_chain_rules()
    grammar222.eliminate_unreachable()
    grammar222.eliminate_non_generating()
    grammar222.eliminate_left_factoring()
    grammar222.eliminate_immediate_left_recursion()
    grammar222.print_grammar()
    # Создадим файл с тестовыми программами
    # test_programs = """
    # program var
    #     a, b, c: %;
    # begin
    #     a ass 5;
    #     b ass 3;
    #     c ass (a + b) * 2;
    #     write(c)
    # end.

    # program var
    #     a, b: %;
    # begin
    #     a ass 10;
    #     b ass 20;
    #     if a < b then
    #         write(a)
    #     else
    #         write(b)
    # end.

    # program var
    #     flag1, flag2: $;
    # begin
    #     flag1 ass true;
    #     flag2 ass not flag1;
    #     write(flag2)
    # end.

    # program var
    #     x, y: %; result: $;
    # begin
    #     x ass 5;
    #     y ass 10;
    #     result ass (x < y) and (y > 0);
    #     write(result)
    # end.

    # program var
    #     a, b, c: $;
    # begin
    #     a ass true;
    #     b ass false;
    #     c ass a or b;
    #     write(c)
    # end.

    # program var
    #     a, b, c: !;
    # begin
    #     a ass 10.0;
    #     b ass 3.0;
    #     c ass a / b;
    #     write(c)
    # end.

    # program var
    #     i, sum: %;
    # begin
    #     sum ass 0;
    #     for i ass 1 to 5 do
    #         sum ass sum + i;
    #     write(sum)
    # end.

    # program var
    #     a: %;
    # begin
    #     a ass 5;
    #     while a > 0 do
    #         a ass a - 1;
    #     write(a)
    # end.

    # {9}

    # program var
    #     a, b: %; c: $;
    # begin
    #     a ass 10;
    #     b ass 20;
    #     c ass a <= b;
    #     write(c)
    # end.

    # program var
    #     a, b: %;
    # begin
    #     a ass 10;
    #     b ass 20;
    #     if a < b then
    #         if a = 10 then
    #             write(100)
    #         else
    #             write(200)
    #     else
    #         write(300)
    # end.

    # {11}

    # program var
    #     a, b: %; c: !;
    # begin
    #     a ass 10;
    #     b ass 0;
    #     c ass a / b;
    #     write(c)
    # end.

    # program var
    #     a: %; b: %;
    # begin
    #     a ass 5;
    #     b ass 10;
    #     write(a)
    # end.

    # program var
    #     a: %;
    # begin
    #     a ass 5;
    #     write(a)
    # end.

    # program var
    #     a, b: %;
    # begin
    #     read(a, b);
    #     a ass a + b;
    #     write(a)
    # end.
    # """


    # # Запишем в файл
    # with open('./test_programs.tyap', 'w') as f:
    #     f.write(test_programs)


    # # Функция для тестирования программы на синтаксический разбор
    # def test_syntax(text):
    #     try:
    #         lexer = Lexer(text)
    #         parser = Parser(lexer)
    #         parser.parse()
    #         return "OK"
    #     except Exception as e:
    #         return str(e)
    
    # def test_exec(text):
    #     try:
    #         lexer = Lexer(text)
    #         parser = Parser(lexer)
    #         interpreter = Interpreter(parser)
    #         interpreter.interpret()
    #         return "OK"
    #     except Exception as e:
    #         return str(e)

    # # Разделим по программам (по вхождениям 'program var')
    # program_list = test_programs.strip().split("program var")
    # program_list = ["program var" + p for p in program_list if p.strip()]

    # # Проверим каждую
    # results = [test_syntax(p) for p in program_list]
    # print(results)

    # results1 = [test_exec(p) for p in program_list]
    # print(results1)


if __name__ == '__main__':
    main()
    
{'nonterminals': {'A', 'B', "A'", 'S'}, 
 'terminals': {'a', 'b'}, 
 'productions': {
     'A': [['a', "A'"], ['b', "A'"]], 
     'B': [['b'], ['A', 'B']], 
     'S': [['b'], ['A', 'B']], 
     "A'": [['B', "A'"], []]}, 
 'start_symbol': 'S'}
