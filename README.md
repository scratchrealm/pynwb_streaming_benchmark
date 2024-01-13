# pynwb_streaming_benchmark

The script [main.py](main.py) was run repeatedly in two settings: On dandihub and on a laptop in a home network.
The results are in [results_dandihub.txt](results_dandihub.txt) and [results_home_network.txt](results_home_network.txt), respectively.

Below is a summary of the average timings. My assessment is that remfile appears to be faster for initial load time while fsspec method appears to be faster for reading a 30 second sample of ephys data. On the home network, the fsspec method appears to be substantially slower than the remfile method for the initial load time.

Some limitations:
* Only applied to a single NWB file
* Only ran a limited number of trials
* Only ran on a single home network
* Didn't test ros3 method yet

---
**On dandihub**

Average Initial Load Time:

- fsspec: 7.74 seconds
- remfile: 6.14 seconds

Average 30sec Sample Read Time:
- fsspec: 7.90 seconds
- remfile: 8.20 seconds ​


---

**On Jeremy's Home Network**

Average Initial Load Time:
- fsspec: 37.23 seconds
- remfile: 9.42 seconds

Average 30sec Sample Read Time:
- fsspec: 47.61 seconds
- remfile: 56.95 seconds ​
