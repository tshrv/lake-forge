import argparse
import os
import shutil
import subprocess
import time
from typing import Optional

from loguru import logger

from utils import timeit


@timeit("Data generation")
def main():
    logger.info("Data generation started")
    args = parse_arguments()
    generate_parquet_data(
        data_dir_name=args.data_dir_name, scale_factor=args.scale_factor
    )
    logger.info("Data generation completed")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate TPCH data in Parquet format."
    )
    parser.add_argument(
        "--data-dir-name",
        type=str,
        default=None,
        help=(
            "Name of the output data directory. If not provided, "
            "a unique name will be generated."
        ),
    )
    parser.add_argument(
        "--scale-factor",
        type=int,
        default=1,
        help="Scale factor for data generation (e.g., 1, 10, 100). Default is 1.",
    )
    return parser.parse_args()


def generate_parquet_data(data_dir_name: Optional[str] = None, scale_factor: int = 1):
    """
    Generate data using tpchgen-cli into specified output directory
    with given scale factor. The data will be generated in Parquet format.
    """
    if not data_dir_name:
        data_dir_name = f"data_sf_{scale_factor}_{int(time.time())}"
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


if __name__ == "__main__":
    main()
