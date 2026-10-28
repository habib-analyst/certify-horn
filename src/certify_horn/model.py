"""Synthetic RAG-sufficiency cases.

A case asks: "Of which country is person P a citizen?"
Target atom: citizen(P, ?). The Horn rule is:

    born(P, C) AND capital(C, K)  ->  citizen(P, K)

where C is a variable shared across the rule body: the city in the
birth fact must be the SAME city whose capital fact is used. That
shared-variable binding is exactly what flat predicate coverage
ignores and what Horn closure with unification enforces.

Case kinds (seeded):
- answerable: gold born(P, C*) and gold capital(C*, K*) passages exist.
- twin_missing: one gold passage is removed (unanswerable twin).
- twin_binding: gold capital exists only for a different city C_other,
  so the binding C cannot be satisfied (unanswerable twin).
- entity_soup: passages mention P, C*, K* individually (e.g. "P visited
  C*", "K* is large") but no capital(C*, K*) relation exists
  (unanswerable; the paper's "names every entity yet lacks one
  required fact" trap).

Distractors in every case: capital facts for other cities (predicate
present, entity mismatched), born facts for other persons in C*
(entity mismatched), and capital facts for other cities whose country
is the modal distractor value (so a most-frequent-value answer over
all retrieved passages is usually wrong).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

PERSONS = ["Ana", "Bo", "Cid", "Dee", "Eli", "Fay", "Gus", "Hal"]
CITIES = ["Alba", "Bora", "Celo", "Dora", "Elda", "Faro", "Gala", "Haro"]
COUNTRIES = ["Kest", "Loma", "Nara", "Osta", "Pira", "Runa", "Sova", "Tuma"]


@dataclass(frozen=True)
class Atom:
    pred: str
    args: tuple  # concrete values, or None for a query variable

    def __repr__(self) -> str:  # compact, readable in certificates
        return f"{self.pred}({', '.join('?' if a is None else str(a) for a in self.args)})"


@dataclass(frozen=True)
class Rule:
    body: tuple  # tuple[Atom] with shared variables as strings "?C"
    head: Atom

    def __repr__(self) -> str:
        return " AND ".join(map(str, self.body)) + " -> " + str(self.head)


CITIZEN_RULE = Rule(
    body=(Atom("born", ("?P", "?C")), Atom("capital", ("?C", "?K"))),
    head=Atom("citizen", ("?P", "?K")),
)
RULES = (CITIZEN_RULE,)


@dataclass
class Passage:
    pid: str
    atom: Atom  # the fact this passage asserts (None-atom = non-relational mention)
    mentions: tuple = ()  # entities named without asserting a relation

    def asserts(self) -> bool:
        return self.atom.pred != "mention"


@dataclass
class Case:
    cid: int
    person: str
    city: str
    country: str
    kind: str  # answerable | twin_missing | twin_binding | entity_soup
    answerable: bool
    passages: list = field(default_factory=list)
    gold_answer: str = ""  # "" when unanswerable


def generate_case(seed: int) -> Case:
    rng = random.Random(seed)
    person = rng.choice(PERSONS)
    ci = rng.randrange(len(CITIES))
    city, country = CITIES[ci], COUNTRIES[ci]
    kind = ["answerable", "twin_missing", "twin_binding", "entity_soup"][seed % 4]
    answerable = kind == "answerable"
    passages: list[Passage] = []
    n = 0

    def add(atom, mentions=()):
        nonlocal n
        passages.append(Passage(pid=f"p{n}", atom=atom, mentions=mentions))
        n += 1

    # Distractors first (so gold is never position-privileged).
    others = [c for c in CITIES if c != city]
    rng.shuffle(others)
    for oc in others[:3]:
        add(Atom("capital", (oc, COUNTRIES[CITIES.index(oc)])))
    # Two other-city capitals share one distractor country so the modal
    # all-passages answer is systematically wrong, not random.
    add(Atom("capital", (others[3], "Zora")))
    add(Atom("capital", (others[4], "Zora")))
    for op in rng.sample([p for p in PERSONS if p != person], 2):
        add(Atom("born", (op, city)))
    add(Atom("mention", ()), mentions=(person, city, country))

    if kind in ("answerable", "entity_soup"):
        add(Atom("born", (person, city)))
    if kind == "answerable":
        add(Atom("capital", (city, country)))
    elif kind == "twin_missing":
        # gold born present, gold capital removed (twin); or vice versa.
        if seed % 8 < 4:
            add(Atom("born", (person, city)))
        else:
            add(Atom("capital", (city, country)))
    elif kind == "twin_binding":
        add(Atom("born", (person, city)))
        add(Atom("capital", (others[0], country)))  # right country, wrong city binding
    elif kind == "entity_soup":
        add(Atom("mention", ()), mentions=(person, city))
        add(Atom("mention", ()), mentions=(city, country))
        # Note: no capital(city, country) relation anywhere.

    rng.shuffle(passages)
    for i, p in enumerate(passages):
        p.pid = f"p{i}"
    return Case(
        cid=seed, person=person, city=city, country=country, kind=kind,
        answerable=answerable, passages=passages,
        gold_answer=country if answerable else "",
    )
