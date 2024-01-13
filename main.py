from dataclasses import dataclass
from typing import Optional
import time
from tempfile import TemporaryDirectory
import fsspec
import remfile
import h5py
import pynwb
from fsspec.implementations.cached import CachingFileSystem


class TestNwbFile:
    def __init__(
        self,
        *,
        dandiset_id: str,
        dandiset_version: str,
        asset_path: str,
        asset_id: str,
        s3_url: str,
        neurosift_link: str,
        electrical_series_name: str,
    ) -> None:
        self.dandiset_id = dandiset_id
        self.dandiset_version = dandiset_version
        self.asset_path = asset_path
        self.asset_id = asset_id
        self.s3_url = s3_url
        self.neurosift_link = neurosift_link
        self.electrical_series_name = electrical_series_name

        self.fsspec_result = TestResult()
        self.remfile_result = TestResult()


@dataclass
class TestResult:
    initial_load_time: Optional[float] = None  # seconds
    sample_30sec_read_time: Optional[float] = None  # seconds


test_nwb_files = [
    TestNwbFile(
        dandiset_id="000409",
        dandiset_version="draft",
        asset_path="sub-CSHL047/sub-CSHL047_ses-2d5f6d81-38c4-4bdc-ac3c-302ea4d5f46e_behavior+ecephys+image.nwb",
        asset_id="88268258-ef35-404c-a946-d4adb6b4237f",
        s3_url="https://dandiarchive.s3.amazonaws.com/blobs/e69/971/e69971fa-a009-4edc-8110-978fbeda67c7",
        neurosift_link="https://flatironinstitute.github.io/neurosift/?p=/nwb&url=https://api.dandiarchive.org/api/assets/88268258-ef35-404c-a946-d4adb6b4237f/download/&dandisetId=000409&dandisetVersion=draft",
        electrical_series_name="ElectricalSeriesAp00",
    ),
]


def main():
    for test_nwb_file in test_nwb_files:
        run_test_on_nwb_file(test_nwb_file)

    # Print results
    print("========================================")
    print("Results:")
    for test_nwb_file in test_nwb_files:
        print(
            f"{test_nwb_file.dandiset_id}/{test_nwb_file.dandiset_version}/{test_nwb_file.asset_path}"
        )
        print("Initial load time:")
        print(f"  fsspec: {test_nwb_file.fsspec_result.initial_load_time}")
        print(f"  remfile: {test_nwb_file.remfile_result.initial_load_time}")
        print("30sec sample read time:")
        print(f"  fsspec: {test_nwb_file.fsspec_result.sample_30sec_read_time}")
        print(f"  remfile: {test_nwb_file.remfile_result.sample_30sec_read_time}")
        print("")


def run_test_on_nwb_file(testfile: TestNwbFile):
    print("========================================")
    print(
        f"Testing {testfile.dandiset_id}/{testfile.dandiset_version}/{testfile.asset_path}"
    )
    for method in ["fsspec", "remfile"]:
        print(f"Testing method {method}")
        if method == "fsspec":
            timer = time.time()
            with TemporaryDirectory() as tmpdir:
                fs = fsspec.filesystem("http")
                fs = CachingFileSystem(
                    fs=fs,
                    cache_storage=tmpdir + "/nwb-cache",  # Local folder for the cache
                )
                with fs.open(testfile.s3_url, "rb") as f:
                    with h5py.File(f) as file:
                        with pynwb.NWBHDF5IO(file=file, load_namespaces=True) as io:
                            nwbfile = io.read()
                            elapsed = time.time() - timer
                            testfile.fsspec_result.initial_load_time = elapsed
                            print(f"Elapsed time for initial load: {elapsed}")
                            run_further_timing_tests(
                                nwbfile,
                                testfile.fsspec_result,
                                electrical_series_name=testfile.electrical_series_name,
                            )
        elif method == "remfile":
            timer = time.time()
            rem_file = remfile.File(testfile.s3_url)
            with h5py.File(rem_file, "r") as h5py_file:
                with pynwb.NWBHDF5IO(file=h5py_file, load_namespaces=True) as io:
                    io.read()
                    elapsed = time.time() - timer
                    testfile.remfile_result.initial_load_time = elapsed
                    print(f"Elapsed time for initial load: {elapsed}")
                    run_further_timing_tests(
                        io.read(),
                        testfile.remfile_result,
                        electrical_series_name=testfile.electrical_series_name,
                    )


def run_further_timing_tests(
    nwbfile: pynwb.NWBFile, result: TestResult, *, electrical_series_name: str
):
    if electrical_series_name:
        print(f'Reading 30sec sample of "{electrical_series_name}"')
        timer = time.time()
        nwbfile.acquisition[electrical_series_name].data[: 30000 * 30]
        elapsed = time.time() - timer
        print(f"Elapsed time for reading 30sec sample: {elapsed}")
        result.sample_30sec_read_time = elapsed


if __name__ == "__main__":
    main()
