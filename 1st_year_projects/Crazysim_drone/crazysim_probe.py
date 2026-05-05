# AI-assisted learning script connects to CrazySim/Crazyflie and retrieves
# basic log data to understand the syntax, GUI communication, and data retrieval.
# Its main purpose was to teach me the basic syntax and process to connect to a Crazyflie drone

import argparse
import logging
import queue
import sys

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="udp://127.0.0.1:19850")
    parser.add_argument("--rw-cache", default="./cache")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    cflib.crtp.init_drivers()

    log_config = LogConfig(name="Probe", period_in_ms=100)
    log_config.add_variable("pm.vbat", "float")
    log_config.add_variable("stabilizer.roll", "float")
    log_config.add_variable("stabilizer.pitch", "float")
    log_config.add_variable("stabilizer.yaw", "float")
    samples: queue.Queue[tuple[int, dict[str, float]]] = queue.Queue()

    def on_sample(ts, data, _logconf):
        samples.put((ts, data))

    try:
        with SyncCrazyflie(args.uri, cf=Crazyflie(rw_cache=args.rw_cache)) as scf:
            print(f"Connected to {args.uri}", flush=True)
            log_config.data_received_cb.add_callback(on_sample)
            scf.cf.log.add_config(log_config)
            log_config.start()
            ts, data = samples.get(timeout=5.0)
            print(f"Timestamp: {ts}", flush=True)
            print(f"Battery: {data['pm.vbat']}", flush=True)
            print(f"Roll: {data['stabilizer.roll']}", flush=True)
            print(f"Pitch: {data['stabilizer.pitch']}", flush=True)
            print(f"Yaw: {data['stabilizer.yaw']}", flush=True)
        return 0
    except Exception as exc:  # pragma: no cover - debug helper
        print(f"Probe failed: {exc}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
