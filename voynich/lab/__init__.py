"""Voynich Lab: hypothesis tests that run on Colab, judged by a council of models.

Every theory module returns a TheoryResult with its own controls: a test only
counts when its positive control succeeds (the method finds the effect when it
is planted) and its negative control fails (it does not find it in shuffled
data). The council of models then discusses the evidence; it never replaces
the numbers.
"""
