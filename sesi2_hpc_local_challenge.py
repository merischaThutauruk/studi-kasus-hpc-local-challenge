"""
Studi Kasus Sesi 2: Bridging Global Infrastructure to Address Local Challenge with HPC
Pemateri: Asst. Prof. Dr. Worawan Diaz Carballo (Thammasat University)
Topik: Komputasi Paralel (Multi-Processing) untuk Co-Simulation Energi Gedung Kampus & Polusi PM2.5
Catatan: Menggunakan Pure Python Standard Library (Zero External Dependencies)
"""

import math
import multiprocessing as mp
import random
import time


def simulate_building_energy_and_pm25(args):
  """Mensimulasikan interaksi agen (mahasiswa/staf), suhu AC (HVAC), dan infiltrasi polusi PM2.5

  dengan operasi matriks floating-point intensif untuk mengukur performa FLOPS.
  """
  building_id, policy_mode, n_hours = args
  rng = random.Random(building_id * 100)

  total_kwh = 0.0
  indoor_pm25_accum = 0.0
  floating_ops_counter = 0

  matrix_size = 20
  thermal_matrix = [
      [rng.uniform(0.8, 1.2) for _ in range(matrix_size)]
      for _ in range(matrix_size)
  ]

  for hour in range(n_hours):
    hour_of_day = hour % 24
    is_weekend = ((hour // 24) % 7) in [5, 6]

    occupants = (
        0
        if (is_weekend or hour_of_day < 7 or hour_of_day > 20)
        else rng.randint(20, 300)
    )
    outdoor_temp = (
        26.0 + 8.0 * math.sin((hour_of_day - 6) * math.pi / 12.0) + rng.gauss(0, 0.5)
    )
    outdoor_pm25 = 45.0 + 35.0 * math.cos(hour_of_day * math.pi / 12.0)

    heat_transfer_sum = 0.0
    for i in range(matrix_size):
      for j in range(matrix_size):
        heat_transfer_sum += thermal_matrix[i][j] * thermal_matrix[j][i]
    heat_transfer_factor = heat_transfer_sum / (matrix_size * matrix_size)
    floating_ops_counter += (2 * matrix_size * matrix_size) + 15

    if policy_mode == "ECO_POLICY":
      ac_active = (not is_weekend) and (9 <= hour_of_day <= 17)
      target_temp = 25.0
    else:
      ac_active = (not is_weekend) and (7 <= hour_of_day <= 21)
      target_temp = 20.0

    if ac_active:
      delta_temp = max(0.0, outdoor_temp - target_temp)
      hvac_power_kw = (
          (delta_temp * 2.8) + (occupants * 0.12) + (heat_transfer_factor * 0.01)
      )
      infiltration_rate = 0.35  
    else:
      hvac_power_kw = 1.5 
      infiltration_rate = 0.75

    total_kwh += hvac_power_kw
    indoor_pm25_accum += outdoor_pm25 * infiltration_rate

  avg_indoor_pm25 = indoor_pm25_accum / n_hours
  return {
      "building_id": f"GEDUNG-{building_id:02d}",
      "policy": policy_mode,
      "total_energy_mwh": total_kwh / 1000.0,
      "estimated_cost_idr": total_kwh * 1444.70,
      "avg_indoor_pm25": avg_indoor_pm25,
      "flops_executed": floating_ops_counter,
  }

def run_hpc_benchmark(n_buildings=12, n_hours=1500):
  print("=== [1] SIMULASI KOMPUTASI HPC & BENCHMARK FLOPS ===")
  tasks_baseline = [(i, "BASELINE", n_hours) for i in range(1, n_buildings + 1)]
  tasks_eco = [(i, "ECO_POLICY", n_hours) for i in range(1, n_buildings + 1)]
  all_tasks = tasks_baseline + tasks_eco

  print(f"Menjalankan {len(all_tasks)} tugas simulasi secara Sekuensial (1 Core)...")
  t0 = time.perf_counter()
  seq_results = [simulate_building_energy_and_pm25(task) for task in all_tasks]
  seq_time = time.perf_counter() - t0

  num_cores = min(mp.cpu_count(), 8)
  print(
      f"Menjalankan {len(all_tasks)} tugas simulasi secara Paralel ({num_cores} Cores)..."
  )
  t1 = time.perf_counter()
  with mp.Pool(processes=num_cores) as pool:
    par_results = pool.map(simulate_building_energy_and_pm25, all_tasks)
  par_time = time.perf_counter() - t1

  total_flops = sum(r["flops_executed"] for r in par_results)
  mflops_achieved = (total_flops / par_time) / 1e6
  speedup = seq_time / par_time if par_time > 0 else 1.0

  print("\n--- HASIL BENCHMARK PERFORMA HPC ---")
  print(f"Waktu Sekuensial (1 Core)     : {seq_time:.4f} detik")
  print(f"Waktu Paralel ({num_cores} Cores)       : {par_time:.4f} detik")
  print(f"Speedup Factor                : {speedup:.2f}x lebih cepat")
  print(f"Total Operasi Floating-Point  : {total_flops:,} FLOPs")
  print(f"Kecepatan Komputasi Paralel   : {mflops_achieved:.2f} MFLOPS\n")

  return par_results

def generate_slurm_script(filename="submit_hpc_job.sh"):
  slurm_content = """#!/bin/bash
#SBATCH --job-name=Campus_CoSim_HPC
#SBATCH --partition=compute
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=16
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --output=cosim_result_%j.out
#SBATCH --error=cosim_error_%j.err

echo "Memulai Job Simulasi Energi & Polusi Lokal pada Superkomputer..."
module load python/3.11
srun python3 sesi2_hpc_local_challenge.py
echo "Job selesai dieksekusi."
"""
  with open(filename, "w", encoding="utf-8") as f:
    f.write(slurm_content)
  print("=== [2] ARTIFACT DESCRIPTION: SLURM SCRIPT ===")
  print(
      f"File '{filename}' berhasil dibuat untuk pengajuan job (sbatch) di klaster HPC Linux.\n"
  )

def evaluate_results(results):
  print("=== [3] EVALUASI DAMPAK LOKAL (KEBIJAKAN ENERGI KAMPUS) ===")
  summary = {}
  for policy in ["BASELINE", "ECO_POLICY"]:
    subset = [r for r in results if r["policy"] == policy]
    total_mwh = sum(r["total_energy_mwh"] for r in subset)
    total_cost_million = sum(r["estimated_cost_idr"] for r in subset) / 1e6
    avg_pm25 = sum(r["avg_indoor_pm25"] for r in subset) / len(subset)
    summary[policy] = {
        "mwh": total_mwh,
        "cost": total_cost_million,
        "pm25": avg_pm25,
    }

  print(
      f"{'KEBIJAKAN':<15} | {'TOTAL ENERGI (MWh)':<20} | {'BIAYA (Juta Rp)':<18} | {'RATA2 PM2.5 (µg/m³)':<20}"
  )
  print("-" * 80)
  for pol, val in summary.items():
    print(
        f"{pol:<15} | {val['mwh']:<20.2f} | Rp {val['cost']:<15.2f} | {val['pm25']:<20.2f}"
    )

  penghematan = summary["BASELINE"]["cost"] - summary["ECO_POLICY"]["cost"]
  print(
      f"\n-> Kesimpulan Integrator: Penerapan ECO_POLICY menghemat biaya listrik sebesar Rp {penghematan:,.2f} Juta!\n"
  )


if __name__ == "__main__":
  results_data = run_hpc_benchmark(n_buildings=12, n_hours=1500)
  evaluate_results(results_data)
  generate_slurm_script()