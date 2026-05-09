import os
import shutil
import subprocess

from loguru import logger

from utils import timeit


@timeit("Data generation")
def generate_parquet_data(scale_factor: int = 1):
    """
    Generate data using tpchgen-cli into specified output directory
    with given scale factor. The data will be generated in Parquet format.
    """
    data_dir_name = f"data_sf_{scale_factor}"
    output_dir = f"./data/{data_dir_name}"

    # delete directory if it already exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # run generator
    result = subprocess.run(
        [
            "uv",
            "run",
            "tpchgen-cli",
            "--scale-factor",
            str(scale_factor),
            "--output-dir",
            output_dir,
            "--format",
            "parquet",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    # log results
    logger.info(f"STDOUT: {result.stdout or None}")
    logger.info(f"Output directory: {output_dir}")
    if result.returncode != 0:
        logger.error(f"Data generation failed with return code {result.returncode}")
        logger.error(f"Error: {result.stderr}")
        raise RuntimeError("Data generation failed")
    return output_dir
