from typing import Dict

DEFAULT_CONFIG_PATH = "./.pipeline.conf"

qsub_template = (
    "qsub {% if depends_str %}{{ depends_str }}{% endif %} {{ header_file }}"
)

default_env = "nullarbor"

default_pbs_context: Dict[str, str] = {
    "shell": "/bin/sh",
    "job_name": "Pypes job",
    "walltime": "04:00:00",
    "ncpus": "4",
    "join": "oe",
    "conda_env": default_env,
}

header_template = """
#PBS -S {{ shell }}
#PBS -N {{ job_name }}
#PBS -l walltime={{ walltime }}
#PBS -l ncpus={{ ncpus }}
#PBS -j {{ join }}
{% if email %}#PBS -M {{ email }}
{% if notify %}#PBS -m {{ notify }}{% endif %}
{% endif %}

# handle work dir
if [ ! $PBS_O_WORKDIR ]
    then
        PBS_O_WORKDIR="$PWD"
fi
cd $PBS_O_WORKDIR

# load module
. /etc/profile.d/modules.sh

{% if conda_env %}
module load python/miniconda
conda activate {{ conda_env }}
{% endif %}

{% if load_module %}
module load {{ load_module }}
{% endif %}

{{ command }}
ret_code=$?

# deactivate conda
conda deactivate

exit $ret_code
"""
