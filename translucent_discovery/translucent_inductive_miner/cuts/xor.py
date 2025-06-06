'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from abc import ABC
from collections import Counter
from typing import Optional, List, Collection, Any, Generic, Dict

from pm4py.util import nx_utils

from pm4py.algo.discovery.inductive.cuts.abc import Cut, T
from translucent_discovery.translucent_inductive_miner.data_structure import IMDataStructureTranslucent
from pm4py.objects.dfg import util as dfu
from pm4py.objects.process_tree.obj import Operator, ProcessTree


class ExclusiveChoiceCut(Cut[T], ABC, Generic[T]):

    @classmethod
    def operator(cls, parameters: Optional[Dict[str, Any]] = None) -> ProcessTree:
        return ProcessTree(operator=Operator.XOR)

    @classmethod
    def holds(cls, obj: T, parameters: Optional[Dict[str, Any]] = None) -> Optional[List[Collection[Any]]]:
        '''
        This method finds a xor cut in the dfg.
        Implementation follows function XorCut on page 188 of
        "Robust Process Mining with Guarantees" by Sander J.J. Leemans (ISBN: 978-90-386-4257-4)

        Basic Steps:
        1.) the dfg is transformed to its undirected equivalent.
        2.) we detect the connected components in the graph.
        3.) if there are more than one connected components, the cut exists and is non-minimal.
        '''
        if parameters["tDFG"]:
            nx_dfg = dfu.as_nx_graph(obj.tdfg)
        else:
            nx_dfg = dfu.as_nx_graph(obj.dfg)
        nx_und = nx_dfg.to_undirected()
        conn_comps = [nx_und.subgraph(c).copy() for c in nx_utils.connected_components(nx_und)]
        if len(conn_comps) > 1:
            cuts = list()
            for comp in conn_comps:
                cuts.append(set(comp.nodes))
            return cuts
        else:
            return None


class ExclusiveChoiceCutTranslucent(ExclusiveChoiceCut[IMDataStructureTranslucent]):
    @classmethod
    def project(cls, obj: IMDataStructureTranslucent, groups: List[Collection[Any]], parameters: Optional[Dict[str, Any]] = None) -> List[IMDataStructureTranslucent]:
        logs = [Counter() for g in groups]
        for t in obj.data_structure:
            count = {i: 0 for i in range(len(groups))}
            for index, group in enumerate(groups):
                for e in t:
                    if e in group:
                        count[index] += 1
            count = sorted(list((x, y) for x, y in count.items()), key=lambda x: (x[1], x[0]), reverse=True)
            new_trace = tuple()
            for e in t:
                if e in groups[count[0][0]]:
                    new_trace = new_trace + (e,)
            logs[count[0][0]].update({new_trace: obj.data_structure[t]})
        return list(map(lambda l: IMDataStructureTranslucent(l, obj.log, frequent=obj.frequent), logs))
