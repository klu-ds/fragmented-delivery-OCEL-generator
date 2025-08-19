# benchmark_runtime.py
import os, shutil, time, itertools, statistics as st, uuid
from dataclasses import dataclass
from typing import List, Dict, Iterable
import numpy as np
import pandas as pd

from .warehouse import Warehouse
from .simulation import Simulation

DELIVERY_FUNCS = {
    "constant": lambda x: 1,
    "quadratic": lambda x: x**2,
    "logarithmic": lambda x: -np.log(x) if x > 0 else 0.0
}

@dataclass
class FixedParams:
    seed: int = 1
    delivery_func_name: str = "constant"
    split_std: float = 1.0
    verbose: bool = False
    write_output: bool = False
    mean_daily_demand: float = 50.0   # <- fixed demand across runs
    std_daily_demand: float = 1.0

def make_sku_configs(
    n_skus: int,
    delivery_func_name: str,
    mean_demand: float,
    std_demand: float,
    split_centre: float,
    split_std: float,
) -> List[Dict]:
    fn = DELIVERY_FUNCS[delivery_func_name]
    configs = []
    for i in range(n_skus):
        configs.append({
            "id": i,
            "rop": 500,
            "eoq": 0,
            "z_score": 1.65,
            "order_base_cost": 60,
            "holding_cost": 1,
            "inventory": 500,
            "delivery_func": fn,
            "kpi": "order_completion",
            "verbose": False,
            # per-SKU demand + split
            "mean_daily_demand": mean_demand,
            "std_daily_demand": std_demand,
            "delivery_split_centre": split_centre,
            "delivery_split_std": split_std,
        })
    return configs

def run_once(days: int, n_skus: int, split_centre: float, fixed: FixedParams) -> Dict:
    wh = Warehouse(
        make_sku_configs(
            n_skus,
            fixed.delivery_func_name,
            fixed.mean_daily_demand,
            fixed.std_daily_demand,
            split_centre,
            split_centre/10,
        )
    )

    out_dir = None
    if fixed.write_output:
        out_dir = f"bench_out_{uuid.uuid4().hex[:8]}"
        os.makedirs(out_dir, exist_ok=True)

    sim_cfg = {
        "warehouse": wh,
        "start_date": pd.Timestamp.now().to_pydatetime(),
        "days": days,
        "seed": fixed.seed,
        "output": out_dir if out_dir else "NO_OUTPUT"
    }

    sim = Simulation(config=sim_cfg)

    t0 = time.perf_counter()
    sim.run()
    sim.evaluate_globally(report=False)
    for sku in wh.SKUs.keys():
        sim.evaluate_skus(sku, report=False)
    t1 = time.perf_counter()

    if out_dir and os.path.isdir(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)

    return {
        "days": days,
        "n_skus": n_skus,
        "split_centre": split_centre,
        "runtime_s": t1 - t0
    }

def run_grid(days_list: Iterable[int], skus_list: Iterable[int], split_list: Iterable[float],
             repeats: int, fixed: FixedParams, on_progress=None) -> pd.DataFrame:
    rows = []
    total_runs = len(days_list) * len(skus_list) * len(split_list) * repeats
    run_count = 0
    _ = run_once(days_list[0], skus_list[0], split_list[0], fixed)  # warmup

    for days, n_skus, split_centre in itertools.product(days_list, skus_list, split_list):
        reps = []
        for r in range(repeats):
            res = run_once(days, n_skus, split_centre, fixed)
            res["repeat"] = r
            rows.append(res)
            reps.append(res["runtime_s"])
            run_count += 1

            if on_progress is not None:
                on_progress((str(run_count), str(total_runs)))
        print(f"[{days}d, {n_skus} SKUs, split={split_centre}] "
              f"-> {st.mean(reps):.3f}s avg over {repeats} runs")
        
    
    return pd.DataFrame(rows)

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["days", "n_skus", "split_centre"])
    out = g["runtime_s"].agg(["count", "mean", "std"]).reset_index()
    out["ci95"] = out.apply(
        lambda r: 1.96 * (r["std"] / (r["count"] ** 0.5)) if r["count"] > 1 and r["std"] == r["std"] else 0.0,
        axis=1
    )
    return out

def main():
    days_list = [250, 500, 1000, 2000]
    skus_list = [1, 5, 10, 20]
    split_list = [0, 1, 2, 5]  
    repeats = 3

    fixed = FixedParams(seed=1, delivery_func_name="constant", split_std=1.0, verbose=False, write_output=False)

    df = run_grid(days_list, skus_list, split_list, repeats, fixed)
    df.to_csv("benchmark_runs_raw.csv", index=False)
    summary = summarize(df)
    summary.to_csv("benchmark_runs_summary.csv", index=False)

    print("\n=== Pivot (mean runtime in seconds) ===")
    print(summary.pivot_table(index=["days"], columns=["n_skus"], values="mean").round(3))

if __name__ == "__main__":
    main()
