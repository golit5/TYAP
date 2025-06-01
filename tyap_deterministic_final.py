# Полная связка: Lexer + LL(1) Parser с тестами
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Set
import sys
from enum import Enum, auto
from copy import deepcopy
from typing import List, Dict, Set
from itertools import zip_longest
from itertools import chain, combinations
import copy

from copy import deepcopy
from typing import Dict, List, Set
from itertools import zip_longest

class Grammar:
    def __init__(self, grammar: Dict):
        self.non_terminals = set(grammar['nonterminals'])
        self.terminals = set(grammar['terminals'])
        self.start_symbol = grammar['start_symbol']
        self.productions = deepcopy(grammar['productions'])

    def toDict(self):
        return {
            "nonterminals": self.non_terminals,
            "terminals": self.terminals,
            "start_symbol": self.start_symbol,
            "productions": self.productions
        }
        
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
        preserve_nullable = {
            "оператор_список", "сумма_хвост", "произведение_хвост", 
            "описание_хвост", "ввода_хвост", "вывода_хвост", 
            "текст_комментария", "ид_хвост", "комментарий"
        }

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
                if not body:
                    if head in preserve_nullable:
                        new_bodies.add(tuple())
                    continue
                
                nullable_indices = [i for i, sym in enumerate(body) if sym in nullable]
                for mask in range(1 << len(nullable_indices)):
                    new_body = []
                    include = [bool((mask >> i) & 1) for i in range(len(nullable_indices))]
                    for i, sym in enumerate(body):
                        if i not in nullable_indices or include[nullable_indices.index(i)]:
                            new_body.append(sym)
                    if new_body or head in preserve_nullable:
                        new_bodies.add(tuple(new_body))
            
            new_productions[head] = [list(b) for b in new_bodies if b or head in preserve_nullable]

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
        
        print(f" Стартовый символ: {self.start_symbol}")

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


        new_nt_index = 0
        
    def eliminate_left_factoring(self):
            """
            Алгоритм 4.6: Устранение левой факторизации правил.
            """
            print("\n2.5 Устранение левой факторизации (алгоритм 4.6):")
            # Сбрасываем индекс для новых нетерминалов
            new_nt_index = 0  # <-- Добавлено: сброс индекса
            new_productions = copy.deepcopy(self.productions)  # <-- Используем глубокую копию
            changed = True

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

            # Обновляем грамматику
            self.productions = new_productions
            self.non_terminals = set(new_productions.keys())
            self.terminals = self._collect_terminals()

            # Вывод результатов
            print(f" Множество нетерминалов: {', '.join(sorted(new_productions.keys()))}")
            print(" Новые правила без одинаковых префиксов:")
            for A in sorted(new_productions.keys()):
                productions = new_productions[A]
                print(f"  {A} -> ", end="")
                for i, prod in enumerate(productions):
                    if i > 0:
                        print(" | ", end="")
                    print(" ".join(prod) if prod else "ε", end="")
                print()

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


# ---------- Лексер ----------
KEYWORDS = {
    "program", "var", "begin", "end", "read", "write",
    "if", "then", "else", "while", "do", "true", "false", "for", "to", "ass"
}

DELIMITERS = {
    '(', ')', ',', ';', ':', '=', '.', '{', '}', '+', '-', '*', '/', '>', '<', "<=", ">=", ":="
}

DATA_TYPES = {"%", "!", "$"}

MULTI_CHAR_DELIMS = {"<=", ">="}

class LexerFA:
    def __init__(self):
        self.identifier_table = {}
        self.identifier_hash = {}
        self.tokens = []
        self.token_types = []

    def hash_id(self, ident):
        return hash(ident) % 997

    def add_identifier(self, ident):
        idx = self.hash_id(ident)
        if ident not in self.identifier_hash:
            self.identifier_hash[ident] = idx
            self.identifier_table[idx] = ident
            print(f"[HASH] Added identifier '{ident}' with hash {idx}")
        return idx

    def lex(self, text):
        i = 0
        state = 'START'
        buffer = ''
        while i < len(text):
            c = text[i]
            if state == 'START':
                if c.isspace():
                    i += 1
                    continue
                elif c.isalpha():
                    buffer = c
                    state = 'ID'
                    i += 1
                elif c.isdigit():
                    buffer = c
                    state = 'NUM'
                    i += 1
                elif c == '{':
                    state = 'COMMENT'
                    i += 1
                elif c in DATA_TYPES:
                    self.tokens.append(c)
                    self.token_types.append('DATA_TYPE')
                    print(f"[LEX] DATA_TYPE: '{c}'")
                    i += 1
                elif c in {':', '<', '>'}:
                    buffer = c
                    state = 'POSSIBLE_DOUBLE'
                    i += 1
                elif c in DELIMITERS:
                    self.tokens.append(c)
                    self.token_types.append('DELIM')
                    print(f"[LEX] DELIMITER: '{c}'")
                    i += 1
                else:
                    print(f"[ERR] Unknown character: '{c}'")
                    i += 1

            elif state == 'ID':
                if c.isalnum() or c == '_':
                    buffer += c
                    i += 1
                else:
                    if buffer in KEYWORDS:
                        self.tokens.append(buffer)
                        self.token_types.append('KW')
                        print(f"[LEX] KEYWORD: '{buffer}'")
                    else:
                        idx = self.add_identifier(buffer)
                        self.tokens.append('идентификатор')
                        self.token_types.append('ID')
                        print(f"[LEX] IDENTIFIER: '{buffer}' (index {idx})")
                    buffer = ''
                    state = 'START'

            elif state == 'NUM':
                if c.isdigit():
                    buffer += c
                    i += 1
                else:
                    self.tokens.append('число')
                    self.token_types.append('NUM')
                    print(f"[LEX] NUMBER: '{buffer}'")
                    buffer = ''
                    state = 'START'

            elif state == 'COMMENT':
                if c == '}':
                    state = 'START'
                i += 1

            elif state == 'POSSIBLE_DOUBLE':
                if (buffer + c) in MULTI_CHAR_DELIMS:
                    self.tokens.append(buffer + c)
                    self.token_types.append('DELIM')
                    print(f"[LEX] MULTI-DELIMITER: '{buffer + c}'")
                    i += 1
                else:
                    self.tokens.append(buffer)
                    self.token_types.append('DELIM')
                    print(f"[LEX] SINGLE-DELIMITER: '{buffer}'")
                buffer = ''
                state = 'START'

        # Конец
        if state == 'ID':
            if buffer in KEYWORDS:
                self.tokens.append(buffer)
                self.token_types.append('KW')
                print(f"[LEX] KEYWORD: '{buffer}'")
            else:
                idx = self.add_identifier(buffer)
                self.tokens.append('идентификатор')
                self.token_types.append('ID')
                print(f"[LEX] IDENTIFIER: '{buffer}' (index {idx})")

        elif state == 'NUM':
            self.tokens.append('число')
            self.token_types.append('NUM')
            print(f"[LEX] NUMBER: '{buffer}'")

    def get_token_stream(self):
        return self.tokens

    def get_identifier_table(self):
        return self.identifier_table


# ---------- LL(1) Parser ----------
class LL1Parser:
    def __init__(self, grammar: Dict):
        self.nonterminals = grammar['nonterminals']
        self.terminals = grammar['terminals']
        self.start_symbol = grammar['start_symbol']
        self.productions = grammar['productions']
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.table = defaultdict(dict)
        self.build()

    def build(self):
        self.compute_first_sets()
        self.compute_follow_sets()
        self.build_parse_table()

    def compute_first_sets(self):
        # Инициализация FIRST для терминалов
        for t in self.terminals:
            self.first[t].add(t)
        
        # Вычисление FIRST для нетерминалов
        changed = True
        while changed:
            changed = False
            for nt in self.nonterminals:
                for prod in self.productions.get(nt, []):
                    # Для каждой продукции A -> α
                    before = len(self.first[nt])
                    
                    # Если α = ε, добавляем ε в FIRST(A)
                    if not prod:
                        self.first[nt].add('ε')
                    else:
                        # Добавляем FIRST(α) в FIRST(A)
                        all_epsilon = True
                        for symbol in prod:
                            self.first[nt].update(self.first[symbol] - {'ε'})
                            if 'ε' not in self.first[symbol]:
                                all_epsilon = False
                                break
                        
                        if all_epsilon:
                            self.first[nt].add('ε')
                    
                    if len(self.first[nt]) > before:
                        changed = True

    def compute_follow_sets(self):
        self.follow[self.start_symbol].add('$')
        
        changed = True
        while changed:
            changed = False
            for nt in list(self.nonterminals):  # Используем list для фиксированного порядка
                for prod in self.productions.get(nt, []):
                    trailer = set(self.follow[nt])
                    
                    # Обрабатываем продукцию в обратном порядке
                    for symbol in reversed(prod):
                        if symbol in self.nonterminals:
                            before = len(self.follow[symbol])
                            self.follow[symbol].update(trailer)
                            if len(self.follow[symbol]) > before:
                                changed = True
                            
                            if 'ε' in self.first[symbol]:
                                trailer.update(self.first[symbol] - {'ε'})
                            else:
                                trailer = set(self.first[symbol])
                        else:
                            trailer = set(self.first[symbol])

    def build_parse_table(self):
        self.table = defaultdict(dict)
        
        for nt in self.nonterminals:
            for prod in self.productions.get(nt, []):
                first_alpha = self.first_of_sequence(prod)
                
                # Для каждого терминала в FIRST(α)
                for terminal in first_alpha - {'ε'}:
                    if terminal in self.table[nt]:
                        # Вместо вызова ошибки, выбираем последнее правило (можно изменить логику)
                        print(f"Предупреждение: конфликт в таблице разбора для {nt} -> {terminal}")
                        print(f"Существующее: {self.table[nt][terminal]}, новое: {prod}")
                    self.table[nt][terminal] = prod
                
                # Если ε в FIRST(α), добавляем для всех терминалов из FOLLOW(A)
                if 'ε' in first_alpha:
                    for terminal in self.follow[nt]:
                        if terminal in self.table[nt]:
                            print(f"Предупреждение: конфликт в таблице разбора для {nt} -> {terminal}")
                            print(f"Существующее: {self.table[nt][terminal]}, новое: {prod}")
                        self.table[nt][terminal] = prod

    def first_of_sequence(self, symbols: List[str]) -> Set[str]:
        result = set()
        for symbol in symbols:
            result.update(self.first[symbol] - {'ε'})
            if 'ε' not in self.first[symbol]:
                return result
        result.add('ε')
        return result

    def parse(self, tokens: List[str]) -> List[Tuple[str, List[str]]]:
        stack = deque(["$", self.start_symbol])
        tokens.append("$")
        cursor = 0
        output = []
        
        while stack:
            top = stack.pop()
            current_token = tokens[cursor]
            
            if top == current_token:
                cursor += 1
            elif top in self.terminals:
                raise SyntaxError(f"Неожиданный токен: {current_token}, ожидался: {top}")
            elif current_token in self.table[top]:
                prod = self.table[top][current_token]
                output.append((top, prod))
                for sym in reversed(prod):
                    if sym != 'ε':
                        stack.append(sym)
            else:
                expected = list(self.table[top].keys())
                raise SyntaxError(f"Неожиданный токен: {current_token} при разборе {top}. Ожидалось: {expected}")
        
        if cursor != len(tokens):
            raise SyntaxError("Входные данные не полностью обработаны")
        return output

# ---------- Пример грамматики и тест ----------
if __name__ == '__main__':
    grammar = {
    "nonterminals": {
        "программа", "описание", "тело", "оператор", "присваивания", "условный",
        "цикла", "цикла_фиксированный", "составной", "ввода", "вывода", "выражение", 
        "сумма", "произведение", "множитель", "унарное", 
        "логическая_константа", "описание_хвост", "оператор_список", "тип",
        "знак_сравнения", "сумма_хвост", "произведение_хвост", "ид_хвост",
        "ввода_хвост", "вывода_хвост", "буква", "цифра", "комментарий"
    },
    "terminals": {
        "program", "var", "begin", "end", "%", "!", "$", "read", "write", "if", "then",
        "else", "while", "do", "for", "to", "true", "false", "not", "ass", "=", "<", ">", 
        "<=", ">=", "+", "-", "*", "/", "or", "and", "(", ")", ",", ":", ";", ".", "a", 
        "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", 
        "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", 
        "7", "8", "9", "{", "}", "идентификатор", "число"
    },
    "start_symbol": "программа",
    "productions": {
        # Основные конструкции
        "программа": [["program", "описание", ";", "тело", "."], ["комментарий", "program", "описание", ";", "тело", "."]],
        "описание": [["var", "идентификатор", "описание_хвост"]],
        "описание_хвост": [[",", "идентификатор", "описание_хвост"], [":", "тип"]],
        "тип": [["%"], ["!"], ["$"]],
        
        # Тело и операторы
        "тело": [["begin", "оператор_список", "end"], ["комментарий", "begin", "оператор_список", "end"]],
        "оператор_список": [["оператор", ";", "оператор_список"], []],
        "оператор": [["присваивания"], ["условный"], ["цикла"], ["цикла_фиксированный"], ["составной"], ["ввода"], ["вывода"], ["комментарий"]],
        
        # Операторы
        "присваивания": [["идентификатор", "ass", "сумма"]],
        "условный": [["if", "выражение", "then", "оператор", "else", "оператор"], ["if", "выражение", "then", "оператор"]],
        "цикла": [["while", "выражение", "do", "оператор"]],
        "цикла_фиксированный": [["for", "присваивания", "to", "выражение", "do", "оператор"]],
        "составной": [["begin", "оператор_список", "end"]],
        "ввода": [["read", "(", "идентификатор", "ввода_хвост", ")"]],
        "ввода_хвост": [[",", "идентификатор", "ввода_хвост"], []],
        "вывода": [["write", "(", "выражение", "вывода_хвост", ")"]],
        "вывода_хвост": [[",", "выражение", "вывода_хвост"], []],
        
        # Выражения
        "выражение": [["унарное"], ["сумма"], ["логическая_константа"]],
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
        "идентификатор": [["идентификатор"]],
        "ид_хвост": [["буква", "ид_хвост"], ["цифра", "ид_хвост"], []],
        "число": [["число"]],
        "логическая_константа": [["true"], ["false"]],
        "буква": [[c] for c in "abcdefghijklmnopqrstuvwxyz"],
        "цифра": [[d] for d in "0123456789"],
        
        # Комментарии
        "комментарий": [["{", "текст_комментария", "}"]],
        "текст_комментария": [["символ", "текст_комментария"], []],
        "символ": [[c] for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ \t\n"]
    }
    }

    grammar222 = Grammar(grammar)
    grammar222.print_grammar()

    # Новый порядок преобразований:
    if not grammar222.check_language_existence():
        raise ValueError("Язык грамматики пуст")

    grammar222.eliminate_non_generating()
    grammar222.eliminate_unreachable()
    grammar222.remove_epsilon_rules()
    grammar222.eliminate_chain_rules()
    grammar222.eliminate_left_factoring()
    grammar222.eliminate_immediate_left_recursion()

    grammar222.print_grammar()



    parser = LL1Parser(grammar222.toDict())

    code = "program var a, b: %; begin a ass 1; end."
    lexer = LexerFA()
    lexer.lex(code)
    tokens = lexer.get_token_stream()

    print("\n[RESULT] Tokens:", tokens)
    print("\n[RESULT] Identifiers:", lexer.get_identifier_table())
    

    #parser = LL1Parser(grammar)
    try:
        result = parser.parse(tokens)
        print("\n[SUCCESS] Parse steps:")
        for lhs, rhs in result:
            print(f"{lhs} -> {' '.join(rhs)}")
    except SyntaxError as e:
        print("\n[ERROR]", e)
