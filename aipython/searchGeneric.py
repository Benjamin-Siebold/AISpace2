# searchGeneric.py - Generic Searcher, including depth-first and A*
# AIFCA Python3 code Version 0.7.1 Documentation at http://aipython.org

# Artificial Intelligence: Foundations of Computational Agents
# http://artint.info
# Copyright David L Poole and Alan K Mackworth 2017.
# This work is licensed under a Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# See: http://creativecommons.org/licenses/by-nc-sa/4.0/deed.en

import heapq  # part of the Python standard library

from aipython import searchProblem
from aipython.searchProblem import (Frontier, Path,
                                    Search_problem_from_explicit_graph)
from aispace2.jupyter.search import Displayable, visualize


class Searcher(Displayable):
    """returns a searcher for a problem.
    Paths can be found by repeatedly calling search().
    This does depth-first search unless overridden
    """

    def __init__(self, problem):
        """creates a searcher from a problem
        """
        self.problem = problem
        self.initialize_frontier()
        self.num_expanded = 0
        self.add_to_frontier(Path(problem.start_node()))
        self.layout_method = "force" if isinstance(
            problem, Search_problem_from_explicit_graph) else "tree"
        super().__init__()

    def initialize_frontier(self):
        self.frontier = []

    def empty_frontier(self):
        return self.frontier == []

    def add_to_frontier(self, path):
        self.frontier.append(path)

    @visualize
    def search(self):
        """returns (next) path from the problem's start node
        to a goal node.
        Returns None if no path exists.
        """
        self.display(2, "Ready")
        while not self.empty_frontier():
            path = self.frontier.pop()
            self.display(2, "Expanding: ", path, "(cost:", path.cost, ")")
            self.num_expanded += 1
            if self.problem.is_goal(path.end()):    # solution found
                # self.display(1, self.num_expanded, "paths have been expanded and", len(self.frontier), "paths remain in the frontier", "\nPath found: ", path)
                self.display(1, "Solution found:", path,
                             "(cost:", path.cost, ")")
                self.solution = path   # store the solution found
            else:
                neighs = self.problem.neighbors(path.end())
                self.display(3, "Neighbors are", neighs)
                for arc in reversed(neighs):
                    self.add_to_frontier(Path(path, arc))
                self.display(3, "Frontier:", self.frontier)
        self.display(1, "No more solutions since the frontier is empty. Total of",
                     self.num_expanded, "paths expanded.")


class AStarSearcher(Searcher):
    """returns a searcher for a problem.
    Paths can be found by repeatedly calling search().
    """

    def __init__(self, problem):
        self.a_star = True
        super().__init__(problem)

    def initialize_frontier(self):
        self.frontier = Frontier()

    def empty_frontier(self):
        return self.frontier.empty()

    def add_to_frontier(self, path):
        """add path to the frontier with the appropriate cost"""
        value = path.cost + self.problem.heuristic(path.end())
        self.frontier.add(path, value)


def test(SearchClass):
    print("Testing problem 1:")
    schr1 = SearchClass(searchProblem.search_simple1)
    path1 = schr1.search()
    print("Path found: ", path1)
    assert list(path1.nodes()) == [
        'g', 'd', 'c', 'b', 'a'], "Shortest path not found in search_simple1"
    print("Passed unit test")


if __name__ == "__main__":
    # test(Searcher)
    test(AStarSearcher)

# example queries:
# searcher1 = Searcher(searchProblem.search_acyclic_delivery)
# searcher1.search()  # find first path
# searcher1.search()  # find next path
# searcher2 = AStarSearcher(searchProblem.search_acyclic_delivery)
# searcher2.search()  # find first path
# searcher2.search()  # find next path
# searcher3 = Searcher(searchProblem.search_cyclic_delivery)
# searcher3.search()  # find first path.  What do you expect to happen?
# searcher4 = AStarSearcher(searchProblem.search_cyclic_delivery)
# searcher4 = AStarSearcher(searchProblem.search_cyclic_delivery)
# searcher4.search()  # find first path
