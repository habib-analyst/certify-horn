"""Horn closure (with unification) vs propositional closure (no binding).

Entity check: a link (passage -> requirement atom) is accepted only
when every concrete argument of the requirement matches the passage
atom's argument in the same position. Requirement atoms here are the
rule-body atoms with the query person bound, city/country open:
  born(P, ?C) and capital(?C, ?K) -- the city variable is shared.

Unification closure: repeatedly apply a rule when its body atoms
unify with known facts under ONE consistent substitution; the head
under that substitution is derived, with its derivation recorded.
Propositional closure (the CONTROL): a rule fires when every body
predicate is present among known facts, regardless of argument
binding -- the head is derived with the first matching fact's
arguments, i.e. flat predicate coverage dressed as closure.
"""
from __future__ import annotations

from .model import Atom, Rule, RULES


def _unify(pattern: Atom, fact: Atom, subst: dict) -> dict | None:
    """Extend subst so pattern matches fact, or None. Variables are
    strings starting with '?' in pattern args; fact args are concrete."""
    if pattern.pred != fact.pred or len(pattern.args) != len(fact.args):
        return None
    out = dict(subst)
    for p, f in zip(pattern.args, fact.args):
        if isinstance(p, str) and p.startswith("?"):
            if p in out and out[p] != f:
                return None
            out[p] = f
        elif p != f:
            return None
    return out


def _subst(atom: Atom, subst: dict) -> Atom:
    return Atom(atom.pred, tuple(
        subst.get(a, a) if isinstance(a, str) and a.startswith("?") else a
        for a in atom.args))


def horn_closure(facts: list[Atom], rules: tuple[Rule, ...] = RULES):
    """Return (derived set, derivations dict atom -> (rule, body facts))."""
    known = list(facts)
    known_set = set(known)
    deriv: dict[Atom, tuple] = {f: ("passage",) for f in facts}
    changed = True
    while changed:
        changed = False
        for rule in rules:
            # Find one consistent substitution covering the whole body.
            def search(i: int, subst: dict, used: list):
                if i == len(rule.body):
                    return subst, used
                for f in known:
                    s2 = _unify(rule.body[i], f, subst)
                    if s2 is not None:
                        r = search(i + 1, s2, used + [f])
                        if r is not None:
                            return r
                return None

            found = search(0, {}, [])
            if found is not None:
                subst, used = found
                head = _subst(rule.head, subst)
                if head not in known_set:
                    known.append(head)
                    known_set.add(head)
                    deriv[head] = (rule, tuple(used))
                    changed = True
    return known_set, deriv


def propositional_closure(facts: list[Atom], rules: tuple[Rule, ...] = RULES):
    """Same machinery minus binding: a rule fires when each body
    predicate merely occurs, using the first fact per predicate."""
    known = list(facts)
    known_set = set(known)
    deriv: dict[Atom, tuple] = {f: ("passage",) for f in facts}
    changed = True
    while changed:
        changed = False
        for rule in rules:
            used = []
            ok = True
            for pat in rule.body:
                match = next((f for f in known if f.pred == pat.pred), None)
                if match is None:
                    ok = False
                    break
                used.append(match)
            if not ok:
                continue
            # Head args: fill each variable from the first body fact
            # that mentions a value in the same position (binding-blind).
            head_args = []
            for a in rule.head.args:
                if isinstance(a, str) and a.startswith("?"):
                    val = None
                    for pat, f in zip(rule.body, used):
                        for pa, fa in zip(pat.args, f.args):
                            if pa == a:
                                val = fa
                                break
                        if val is not None:
                            break
                    head_args.append(val)
                else:
                    head_args.append(a)
            head = Atom(rule.head.pred, tuple(head_args))
            if head not in known_set:
                known.append(head)
                known_set.add(head)
                deriv[head] = (rule, tuple(used))
                changed = True
    return known_set, deriv


def decide_cert(case, use_unification: bool):
    """Certificate arm decision.

    Retrieval: per requirement, all passages asserting a body predicate.
    Entity check: link accepted only if the passage atom's person (for
    born) matches the query person -- the query-bound argument. Capital
    links are accepted on predicate (city is the open variable the
    closure must bind); the binding discipline lives in unification.
    Returns (decision, answer, certificate_atoms, open_requirements).
    """
    links = []
    for p in case.passages:
        if p.atom.pred == "born" and p.atom.args[0] == case.person:
            links.append(p.atom)
        elif p.atom.pred == "capital":
            links.append(p.atom)
    closure = horn_closure if use_unification else propositional_closure
    derived, deriv = closure(links)
    targets = [a for a in derived if a.pred == "citizen" and a.args[0] == case.person]
    if not targets:
        open_reqs = []
        if not any(a.pred == "born" for a in links):
            open_reqs.append("born(P, ?C)")
        if not any(a.pred == "capital" for a in links):
            open_reqs.append("capital(?C, ?K)")
        if not open_reqs:
            open_reqs.append("citizen(P, ?K) not derivable: rule-body binding unsatisfied")
        return ("abstain", "", [], open_reqs)
    # Certificate: the derivation chain of the first target, minimal set.
    target = targets[0]
    cert = []

    def walk(atom):
        entry = deriv.get(atom)
        if entry is None:
            return
        if entry[0] == "passage":
            cert.append(atom)
        else:
            for b in entry[1]:
                walk(b)

    walk(target)
    return ("answer", target.args[1], cert, [])
