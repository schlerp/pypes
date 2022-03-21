from typing import List

import networkx

from pypes.exceptions import InvalidDAGException
from pypes.models import Pipeline


def pipeline_to_dag(pipeline: Pipeline) -> networkx.MultiDiGraph:
    edge_list = []
    for source in pipeline.steps:
        for target in pipeline.steps:
            for output in source.outputs:
                if source.id == target.id:
                    continue
                for _input in target.inputs:
                    if output.path == _input.path:
                        edge_list.append((source.id, target.id, output.path))
    nodes = [step.id for step in pipeline.steps]
    dag = networkx.MultiDiGraph()
    dag.update(edges=edge_list, nodes=nodes)
    if not networkx.is_directed_acyclic_graph(dag):
        raise InvalidDAGException(
            "Graph contains a cycle! {}".format(networkx.find_cycle(dag))
        )
    return dag


def get_execution_order(dag: networkx.MultiDiGraph) -> List[str]:
    return list(networkx.topological_sort(dag))
