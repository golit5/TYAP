from enum import Enum
from LA import TypeTokens, relationship_ops, addition_ops, multiplication_ops, unary_ops
from itertools import chain, combinations

class Grammar:
    def __init__(self):
        self.productions = {
            # Программа и операторы
            "программа": [ ["{", "последовательность_описаний_и_операторов", "}"] ],

            "последовательность_описаний_и_операторов": [ 
                ["описание", ";", "последовательность_описаний_и_операторов"], 
                ["оператор", ";", "последовательность_описаний_и_операторов"], 
                [] 
            ],
            "оператор": [ ["составной"], ["присваивания"], 
                         ["условный"], ["фиксированного_цикла"], ["условного_цикла"], 
                         ["ввода"], ["вывода"] ],
            
            # Объявления
            "описание": [ ["тип", "идентификаторы"] ],
            "тип": [ ["%"], ["!"], ["$"] ],
            "идентификаторы": [ ["идентификатор", ",", "идентификаторы"], ["идентификатор"] ],
            
            # Операторы
            "составной": [ ["оператор", ":", "составной"], ["оператор"] ],
            "присваивания": [ ["идентификатор", "ass", "выражение"] ],
            "условный": [ ["if", "выражение", "then", "оператор", "else", "оператор"],
                           ["if", "выражение", "then", "оператор"] ],
            "фиксированного_цикла": [ ["for", "присваивания", "to", "выражение", "do", "оператор"] ],
            "условного_цикла": [ ["while", "выражение", "do", "оператор"] ],
            "ввода": [ ["read", "(", "идентификаторы", ")"] ],
            "вывода": [ ["write", "(", "выражения", ")"] ],
            "выражения": [ ["выражение", ",", "выражения"], ["выражение"] ],
            
            # Выражения
            "выражение": [ ["операнд", "операции_отношения"] ],
            "операции_отношения": [ ["операция_отношения", "операнд", "операции_отношения"], [] ],
            "операнд": [ ["слагаемое", "операции_сложения"] ],
            "операции_сложения": [ ["операция_сложения", "слагаемое", "операции_сложения"], [] ],
            "слагаемое": [ ["множитель", "операции_умножения"] ],
            "операции_умножения": [ ["операция_умножения", "множитель", "операции_умножения"], [] ],
            
            # Множители
            "множитель": [ ["идентификатор"], ["число"], ["логическая_константа"], 
                      ["унарная_операция", "множитель"], ["(", "выражение", ")"] ],
            "логическая_константа": [ ["true"], ["false"] ],
            
            # Числа
            "число": [ ["целое"], ["действительное"] ],
            "целое": [ ["двоичное"], ["восьмеричное"], ["десятичное"], ["шестнадцатеричное"] ],
            "двоичное": [ ["двоичные_цифры", "B"], ["двоичные_цифры", "b"] ],
            "восьмеричное": [ ["восьмеричные_цифры", "O"], ["восьмеричные_цифры", "o"] ],
            "десятичное": [ ["цифры", "D"], ["цифры", "d"], ["цифры"] ],
            "шестнадцатеричное": [ ["шестнадцатеричные_цифры", "H"], ["шестнадцатеричные_цифры", "h"] ],
            "действительное": [ ["цифры", ".", "цифры", "порядок"], 
                    ["цифры", "порядок"],
                    ["цифры", ".", "цифры"] ],
            "порядок": [ ["E", "знак", "цифры"], ["e", "знак", "цифры"] ],
            "знак": [ ["+"], ["-"], [] ],
            
            # Терминалы (заполняются из лексического анализатора)
            "операция_отношения": [[op] for op in relationship_ops],
            "операция_сложения": [[op] for op in addition_ops],
            "операция_умножения": [[op] for op in multiplication_ops],
            "унарная_операция": [[op] for op in unary_ops],
            
            # Определение идентификатора по правилу <идентификатор>::= <буква> {<буква> | <цифра>}
            "идентификатор": [["буква", "хвост_идентификатора"]],
            "хвост_идентификатора": [
                ["буква", "хвост_идентификатора"],
                ["цифра", "хвост_идентификатора"],
                []
            ],
            "буква": [
                ["a"], ["b"], ["c"], ["d"], ["e"], ["f"], ["g"], ["h"], ["i"], ["j"], 
                ["k"], ["l"], ["m"], ["n"], ["o"], ["p"], ["q"], ["r"], ["s"], ["t"],
                ["u"], ["v"], ["w"], ["x"], ["y"], ["z"],
                ["A"], ["B"], ["C"], ["D"], ["E"], ["F"], ["G"], ["H"], ["I"], ["J"],
                ["K"], ["L"], ["M"], ["N"], ["O"], ["P"], ["Q"], ["R"], ["S"], ["T"],
                ["U"], ["V"], ["W"], ["X"], ["Y"], ["Z"]
            ],
            "цифра": [
                ["0"], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"], ["8"], ["9"]
            ],
            
            # Определение цифр для различных систем счисления
            "двоичные_цифры": [["двоичная_цифра"], ["двоичная_цифра", "двоичные_цифры"]],
            "двоичная_цифра": [["0"], ["1"]],
            
            "восьмеричные_цифры": [["восьмеричная_цифра"], ["восьмеричная_цифра", "восьмеричные_цифры"]],
            "восьмеричная_цифра": [["0"], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"]],
            
            "цифры": [["цифра"], ["цифра", "цифры"]],
            
            "шестнадцатеричные_цифры": [["шестнадцатеричная_цифра"], ["шестнадцатеричная_цифра", "шестнадцатеричные_цифры"]],
            "шестнадцатеричная_цифра": [
                ["0"], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"], ["8"], ["9"],
                ["a"], ["b"], ["c"], ["d"], ["e"], ["f"],
                ["A"], ["B"], ["C"], ["D"], ["E"], ["F"]
            ]
        }
        
        self.start_symbol = "программа"
        self.non_terminals = set(self.productions.keys())
        self.terminals = self._collect_terminals()
        
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