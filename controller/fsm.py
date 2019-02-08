from collections import defaultdict

_split_n_strip = lambda s, d: [x.strip() for x in s.split(d) if x]

class State(object):
  """Represents a State in the FSM."""
  def __init__(self):
    self.name = ''
    self.transitions = []
 
  def next_state(self, context):
    """Evaluates the next state."""
    for cond, next_state in self.transitions:
      if eval(cond, {}, context):
        return next_state
    return self

class FSM(object):
  """Tiny Graphiz inspired DSL for defining a FSM.

  Syntax:
      # is a comment (obviously)
      from -> to | condition that must evaluate to true to transition
  """

  def __init__(self, desc):
    states = defaultdict(State)
    for line in _split_n_strip(desc, "\n"):
      if line.startswith("#"): continue
      if "->" not in line or "|" not in line:
        raise Error("Invalid line: %s" % line)
      # A -> B | <condition>
      transition, condition = _split_n_strip(line, "|")
      start, end = _split_n_strip(transition, "->")
      states[start].name = start
      states[end].name = end
      states[start].transitions += (condition, states[end]),

    self.states = dict(states)
    self.current = states['uninitialized']

  def evaluate(self, context):
    self.current = self.current.next_state(context)

  def graphviz(self):
    out = []
    for s in self.states.values():
      for c, t in s.transitions:
        out.append("\"%s\" -> \"%s\" [label = \"%s\"]" % (s.name, t.name, c))
    return '\n'.join(out)
