import subprocess
import time
from typing import Optional

from loguru import logger


def main():
    logger.info("Data generation started")
    generate_parquet_data(data_dir_name="data_sf_1", scale_factor=1)
    logger.info("Data generation completed")


def generate_parquet_data(data_dir_name: Optional[str] = None, scale_factor: int = 1):
    """
    Generate data using tpchgen-cli into specified output directory with given scale factor. The data will be generated in Parquet format.
    """
    if not data_dir_name:
        data_dir_name = f"data_sf_{scale_factor}_{int(time.time())}"
    output_dir = f"./data/{data_dir_name}"
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
    logger.info(f"STDOUT: {result.stdout or None}")
    if result.returncode != 0:
        logger.error(f"Data generation failed with return code {result.returncode}")
        logger.error(f"Error: {result.stderr}")


if __name__ == "__main__":
    main()
