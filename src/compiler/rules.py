class Rule:
    def __init__(self, name, start, end=None, interp=None, region=True):
        self.name = name
        self.start = start
        self.end = end if end else start
        self.interp = interp
        self.region = region
    
    def is_region(self):
        return self.region
    
    def __str__(self):
        return f'Rule[{self.name} -> {self.start} {self.end}]'
    
    def __repr__(self):
        return self.__str__()

class RuleCodeChunk:
    def __init__(self, code, file_iter):
        self.code = code
        self.file_iter = file_iter
    
    def get(self):
        index = self.file_iter.get_index()
        return self.code[:index + 1]

class Rules:
    def __init__(self, code, file_iter):
        self.chunk = RuleCodeChunk(code, file_iter)
        self.rules = [
            Rule('global', None, region=False),
            Rule('text_single', '\'', interp='interp'),
            Rule('interp', '{', '}', region=False),
            Rule('comment', '#', '\n'),
            Rule('command', '$', '$', interp='interp'),
        ]
        self.stack = [self.rules[0]]
        self.begin_rules = list(map(lambda r: r.start, self.rules))
        self.end_rules = list(map(lambda r: r.end, self.rules))
    
    def get_rule_by_func(self, func):
        for rule in self.rules:
            if func(rule):
                return rule
        return None

    def get_rule_by_name(self, name):
        return self.get_rule_by_func(lambda r: r.name == name)

    def get_rule_by_tok_str(self, chunk, tok_str):
        is_valid = lambda r: tok_str(r) != None
        is_equal = lambda r: tok_str(r) == chunk[-len(tok_str(r)):]
        is_escaped = lambda r: len(chunk) > len(tok_str(r)) and chunk[-len(tok_str(r)) - 1] == '\\'
        return self.get_rule_by_func(
            lambda r: is_valid(r) and is_equal(r) and not is_escaped(r))

    def get_rule_by_start(self, chunk):
        return self.get_rule_by_tok_str(chunk, lambda r: r.start)

    def get_rule_by_end(self, chunk):
        return self.get_rule_by_tok_str(chunk, lambda r: r.end)

    def is_base_region(self):
        return len(self.stack) == 1

    def is_region(self):
        return self.stack[-1].region

    def get_region(self):
        return self.stack[-1]
    
    def handle_rule(self):
        reg = self.stack[-1]
        # If it's a region - close it
        if reg.is_region():
            # Or if has interpolation sequence - open new
            if reg.interp != None:
                interp = self.get_rule_by_name(reg.interp)
                rule = self.get_rule_by_start(self.chunk.get())
                if rule and rule.start == interp.start:
                    self.stack.append(rule)
                    return True
            rule = self.get_rule_by_end(self.chunk.get())
            if rule and rule.name == reg.name:
                self.stack.pop()
                return True
        else:
            # Check if it's an interpolation and if it can be closed
            if not reg.region and reg.end:
                rule = self.get_rule_by_end(self.chunk.get())
                if rule and rule == reg:
                    self.stack.pop()
                    return True
            rule = self.get_rule_by_start(self.chunk.get())
            if rule:
                self.stack.append(rule)
                return True
        return False

