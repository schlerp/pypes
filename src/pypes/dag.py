from typing import List

import networkx

from pypes.exceptions import InvalidDAGException
from pypes.models import Pipeline


def pipeline_to_dag(pipeline: Pipeline) -> networkx.MultiDiGraph:
    edge_list = []
    for source in pipeline.steps:
        for target in pipeline.steps:
            for output in source.outputs.values():
                if source.name == target.name:
                    continue
                for _input in target.inputs.values():
                    if output == _input:
                        edge_list.append((source.name, target.name, output))
    nodes = [step.name for step in pipeline.steps]
    dag = networkx.MultiDiGraph()
    dag.update(edges=edge_list, nodes=nodes)
    if not networkx.is_directed_acyclic_graph(dag):
        raise InvalidDAGException(
            "Graph contains a cycle! {}".format(networkx.find_cycle(dag))
        )
    return dag


def get_execution_order(dag: networkx.MultiDiGraph) -> List[str]:
    return list(networkx.topological_sort(dag))
