from typing import Callable

from pypes.dag import get_execution_order, pipeline_to_dag
from pypes.exceptions import InvalidDAGException
from pypes.models import Pipeline


def test_create_dag(
    create_split_merge_pipeline: Callable[..., Pipeline],
    cleanup_temp_files: Callable[..., None],
):
    pipeline = create_split_merge_pipeline()
    dag = pipeline_to_dag(pipeline)
    assert dag is not None
    cleanup_temp_files(pipeline.steps)


def test_create_dag_cycle(
    create_split_merge_pipeline: Callable[..., Pipeline],
    cleanup_temp_files: Callable[..., None],
):
    pipeline = create_split_merge_pipeline(should_succeed=False)
    try:
        dag = pipeline_to_dag(pipeline)
        assert False
    except InvalidDAGException:
        assert True
    finally:
        cleanup_temp_files(pipeline.steps)


def test_dag_exec_order_succeed(
    create_split_merge_pipeline: Callable[..., Pipeline],
    cleanup_temp_files: Callable[..., None],
):
    pipeline = create_split_merge_pipeline()
    dag = pipeline_to_dag(pipeline)
    exec_order = get_execution_order(dag)
    assert (
        exec_order.index("step 1")
        < exec_order.index("step 2")
        < exec_order.index("step 3")
    )
    cleanup_temp_files(pipeline.steps)
