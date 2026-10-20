#!/bin/bash
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
