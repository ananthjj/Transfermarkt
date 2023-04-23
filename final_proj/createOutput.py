filename = "test1.txt"
output_file = "output.txt"
suffix = 0

while True:
    try:
        if suffix > 0:
            output_file = f"output{suffix}.txt"
        with open(output_file, 'x') as out_file:
            with open(filename) as in_file:
                for line in in_file:
                    if "profil" in line:
                        out_file.write(line)
            print(f"Data written to {output_file}")
        break
    except FileExistsError:
        suffix += 1
