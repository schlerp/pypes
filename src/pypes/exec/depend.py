from pathlib import Path
from typing import List, Tuple

import networkx
from pypes.exceptions import InvalidDAGException
from pypes.models.pipeline import Pipeline


def pipeline_to_dag(pipeline: Pipeline) -> networkx.MultiDiGraph:
    edge_list: List[Tuple[str, str, str]] = []
    for source in pipeline.steps:
        for target in pipeline.steps:
            for output in source.outputs:
                if source.name == target.name:
                    continue
                for _input in target.inputs:
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


def get_ancestors(dag: networkx.MultiDiGraph, name: str) -> List[str]:
    return [x for x in networkx.ancestors(dag, name)]


def get_descendants(dag: networkx.MultiDiGraph, name: str) -> List[str]:
    return [x for x in networkx.descendants(dag, name)]
