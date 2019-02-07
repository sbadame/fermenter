from collections import defaultdict

_split_n_strip = lambda s, d: [x.strip() for x in s.split(d) if x]

class State(object):
 """Represents a State in the FSM."""
 def __init__(self):
   self.name = ''
   self.transitions = []
   self.on_enter = None

 def next_state(self, context):
   for cond, next_state in self.transitions:
     if eval(cond, {}, context):
       return next_state

class FSM(object):

 def __init__(self, desc):
   states = defaultdict(State)
   for line in _split_n_strip(desc, "\n"):
     if line.startswith("#"): continue
     if ":" in line: # state : <python code>
       state, on_enter = _split_n_strip(line, ":")
       states[state].name = state
       states[state].on_enter = on_enter
     elif "|" in line: # from -> to | <python condition>
       transition, condition = _split_n_strip(line, "|")
       start, end = _split_n_strip(transition, "->")
       states[start].name = start
       states[end].name = end
       states[start].transitions += (condition, states[end]),
     else:
       raise Error("Invalid line: %s" % line)
   self.states = states.values()

  def graphviz(self):
    out = []
    for s in self.states:
      for c, t in s.transitions:
        out.append("\"%s\" -> \"%s\" [label = \"%s\"]" % (s.name, t.name, c))
      if s.on_enter:
        out.append("\"%s\" [label = \"%s\"]" % (s.name, s.on_enter))
    return '\n'.join(out)
    
print(FSM("""
 # Tiny Graphiz inspired DSL for defining a FSM.
 # Syntax:
 #   # is a comment (obviously)
 #   from -> to |  condition that must evaluate to true to transition
 #   state : code to execute when entering the state


 cooling : controller.cool()
 off     : controller.off()
 uninitialized -> off     | temp < desired
 uninitialized -> cooling | temp > desired
 cooling -> off           | temp < desired - threshold
 off -> cooling           | temp > desired + threshold
""").graphviz())

