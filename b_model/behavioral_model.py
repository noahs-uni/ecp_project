import csv

def int_to_bits(x, width):
    return [(x >> i) & 1 for i in range(width)]

def bits_to_int(bits):
    return sum(bit << i for i, bit in enumerate(bits))

def full_adder(a, b, c_in = 0):
    s_out = a ^ b ^ c_in
    c_out = (a & b) | (c_in & (a ^ b))
    return s_out, c_out

def exact_ppu(a, b, c_in = 0, s_in = 0):
    t1 = not (a and b)
    t2 = not (c_in and s_in)
    t3 = not (c_in or s_in)
    t4 = not (t1)
    t5 = not (t2 or t4)
    t6 = not (t1 or t3)
    t7 = not (t5 or t6)
    c_out = not t7

    t8 = s_in ^ c_in
    s_out = t8 ^ t4    
    return s_out, c_out

def approx1_ppu(a, b, c_in = 0, s_in = 0):
    t1 = not (s_in and c_in)
    c_out = not t1

    s_out = c_in ^ s_in    
    return s_out, c_out

def approx2_ppu(a, b, c_in = 0, s_in = 0):
    t1 = not (a and b)
    t2 = not (c_in and s_in)
    t3 = not (c_in or s_in)
    t4 = not (t1)
    t5 = not (t2 or t4)
    t6 = not (t1 or t3)
    t7 = not (t5 or t6)
    c_out = not t7

    t8 = not (t4 and s_in)
    s_out = not (t8 and c_in)
    return s_out, c_out

def approx3_ppu(a, b, c_in = 0, s_in = 0):
    t1 = not (a and b)
    t2 = not (c_in and s_in)
    t3 = not (c_in or s_in)
    t4 = not (t1)
    t5 = not (t2 or t4)
    t6 = not (t1 or t3)
    s_out = not (t5 or t6)
    c_out = not s_out
    return s_out, c_out

def approx4_ppu(a, b, c_in = 0, s_in = 0):
    t1 = not a
    t2 = not (s_in and c_in)
    t3 = not (s_in or c_in)
    t4 = not (t2 or a)
    t5 = not (t1 or t3)
    t6 = not (t4 or t5)
    c_out = not t6

    t7 = s_in ^ c_in
    s_out = t7 ^ a
    return s_out, c_out

ppu_dict = {
    'exact': exact_ppu,
    'approx1': approx1_ppu,
    'approx2': approx2_ppu,
    'approx3': approx3_ppu,
    'approx4': approx4_ppu,
}

def mul(a_int, b_int, ppu_type='exact', WIDTH = 8):
    a = int_to_bits(a_int, WIDTH)
    b = int_to_bits(b_int, WIDTH)

    sum_bits = [[0] * (2 * WIDTH) for _ in range(WIDTH + 1)]
    carry_bits = [[0] * (2 * WIDTH) for _ in range(WIDTH + 1)]

    # Populate first row with and's
    for i in range(WIDTH):
        sum_bits[0][i] = a[i] & b[0]

    # Populate first diagonal column with and's
    for i in range(1, WIDTH):
        sum_bits[i][WIDTH - 1 + i] = a[WIDTH - 1] & b[i]

    # Generate partial products
    for i in range(1, WIDTH):
        for j in range(i, i + WIDTH - 1):
            s, c = ppu_dict[ppu_type](a[j - i], b[i], carry_bits[i - 1][j - 1], sum_bits[i - 1][j])
            sum_bits[i][j] = s
            carry_bits[i][j] = c

    # Final addition
    for i in range(WIDTH, 2 * WIDTH - 1):
        s, c = full_adder(sum_bits[WIDTH - 1][i], carry_bits[WIDTH - 1][i - 1], carry_bits[WIDTH][i - 1]) 
        sum_bits[WIDTH][i] = s
        carry_bits[WIDTH][i] = c

    result_bits = [0] * (2 * WIDTH)
    for i in range(WIDTH):
        result_bits[i] = sum_bits[i][i]

    for i in range(WIDTH, 2 * WIDTH - 1):
        result_bits[i] = sum_bits[WIDTH][i]

    result_bits[2 * WIDTH - 1] = carry_bits[WIDTH][2 * WIDTH - 2]

    return bits_to_int(result_bits)

if __name__ == "__main__":
    for ppu_type in ['exact', 'approx1', 'approx2', 'approx3', 'approx4']:
        WIDTH = 8
        with open(f'LUT_{ppu_type}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header row
            writer.writerow([''] + list(range(256)))
            
            # Write each row with a as row label
            for a in range(pow(2, WIDTH)):
                row = [a]
                for b in range(pow(2, WIDTH)):
                    product = mul(a, b, ppu_type=ppu_type, WIDTH=WIDTH)
                    row.append(product)
                writer.writerow(row)
