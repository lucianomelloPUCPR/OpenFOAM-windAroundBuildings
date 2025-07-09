input_file = 'postProcessing/htc_surfaces/0/wallHeatTransferCoeff.dat'
output_file = 'postProcessing/htc_surfaces/0/wallHeatTransferCoeff.dat'

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
        if line.strip().startswith('#') or not line.strip():
            f_out.write(line)
            continue
        parts = line.split()
        if len(parts) >= 5:
            # Format time and patch as-is, round the next three columns
            time = parts[0]
            patch = parts[1]
            min_val = float(parts[2])
            max_val = float(parts[3])
            avg_val = float(parts[4])
            f_out.write(f"{time}\t{patch}\t{min_val:.1f}\t{max_val:.1f}\t{avg_val:.1f}\n")
        else:
            f_out.write(line)

print(f"✅ Rounded file saved to {output_file}")
