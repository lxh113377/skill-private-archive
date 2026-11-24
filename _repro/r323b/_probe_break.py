# 复刻 frozen_blind_eval.py:70 的判分表达式，用多值 expected 喂它
def line70(top1, expected):
    return (top1 in (None, "NONE")) if expected is None else (top1 == expected)
print("SCALAR_OK", line70("A-ask-questions", "A-ask-questions"))
print("LIST_BREAKS", line70("A-ask-questions", ["A-ask-questions", "brainstorming"]))
print("LIST_BREAKS2", line70("brainstorming", ["A-ask-questions", "brainstorming"]))
print("SET_MEMBERSHIP_WOULD_BE", "A-ask-questions" in {"A-ask-questions","brainstorming"})